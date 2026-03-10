import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Optional

from fastapi import Depends, HTTPException, Request, status


ROLE_LEVELS = {
    "viewer": 1,
    "analyst": 2,
    "admin": 3,
}


@dataclass(frozen=True)
class Principal:
    client_id: str
    role: str
    name: str = "API Client"


@dataclass(frozen=True)
class LimitPolicy:
    requests_per_minute: int
    daily_requests_limit: int
    daily_upload_bytes_limit: int
    daily_analysis_jobs_limit: int


@dataclass(frozen=True)
class ApiKeyConfig:
    key: str
    principal: Principal
    policy: LimitPolicy


def _to_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def is_auth_enabled() -> bool:
    return _to_bool(os.getenv("AUTH_ENABLED"), default=False)


def _default_policy_for_role(role: str) -> LimitPolicy:
    if role == "admin":
        return LimitPolicy(
            requests_per_minute=600,
            daily_requests_limit=200_000,
            daily_upload_bytes_limit=2 * 1024 * 1024 * 1024,
            daily_analysis_jobs_limit=5_000,
        )
    if role == "analyst":
        return LimitPolicy(
            requests_per_minute=180,
            daily_requests_limit=50_000,
            daily_upload_bytes_limit=500 * 1024 * 1024,
            daily_analysis_jobs_limit=1_000,
        )
    return LimitPolicy(
        requests_per_minute=60,
        daily_requests_limit=10_000,
        daily_upload_bytes_limit=100 * 1024 * 1024,
        daily_analysis_jobs_limit=100,
    )


def _parse_policy(raw_entry: Dict[str, object], role: str) -> LimitPolicy:
    defaults = _default_policy_for_role(role)
    return LimitPolicy(
        requests_per_minute=int(raw_entry.get("requests_per_minute", defaults.requests_per_minute)),
        daily_requests_limit=int(raw_entry.get("daily_requests_limit", defaults.daily_requests_limit)),
        daily_upload_bytes_limit=int(raw_entry.get("daily_upload_bytes_limit", defaults.daily_upload_bytes_limit)),
        daily_analysis_jobs_limit=int(raw_entry.get("daily_analysis_jobs_limit", defaults.daily_analysis_jobs_limit)),
    )


def _normalize_role(role: str) -> str:
    normalized = role.strip().lower()
    if normalized not in ROLE_LEVELS:
        raise ValueError(f"Unsupported role: {role}")
    return normalized


@lru_cache(maxsize=1)
def load_api_keys() -> Dict[str, ApiKeyConfig]:
    api_keys: Dict[str, ApiKeyConfig] = {}

    json_payload = os.getenv("API_KEYS_JSON")
    if json_payload:
        entries = json.loads(json_payload)
        if not isinstance(entries, list):
            raise ValueError("API_KEYS_JSON must be a JSON array")

        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("Each API_KEYS_JSON entry must be an object")
            raw_key = str(entry.get("key", "")).strip()
            if not raw_key:
                continue

            role = _normalize_role(str(entry.get("role", "viewer")))
            principal = Principal(
                client_id=str(entry.get("client_id", f"client-{len(api_keys) + 1}")),
                role=role,
                name=str(entry.get("name", "API Client")),
            )
            api_keys[raw_key] = ApiKeyConfig(
                key=raw_key,
                principal=principal,
                policy=_parse_policy(entry, role),
            )

    fallback_key = os.getenv("API_KEY")
    if fallback_key and fallback_key not in api_keys:
        fallback_role = _normalize_role(os.getenv("API_KEY_ROLE", "admin"))
        fallback_principal = Principal(
            client_id=os.getenv("API_KEY_CLIENT_ID", "default-client"),
            role=fallback_role,
            name=os.getenv("API_KEY_NAME", "Default API Key"),
        )
        api_keys[fallback_key] = ApiKeyConfig(
            key=fallback_key,
            principal=fallback_principal,
            policy=_default_policy_for_role(fallback_role),
        )

    return api_keys


def resolve_principal(request: Request) -> tuple[Principal, LimitPolicy]:
    if not is_auth_enabled():
        role = _normalize_role(os.getenv("DEV_DEFAULT_ROLE", "admin"))
        principal = Principal(
            client_id=os.getenv("DEV_CLIENT_ID", "local-dev"),
            role=role,
            name="Local Development",
        )
        return principal, _default_policy_for_role(role)

    api_key = request.headers.get("x-api-key", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    key_map = load_api_keys()
    config = key_map.get(api_key)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return config.principal, config.policy


def get_principal(request: Request) -> Principal:
    principal = getattr(request.state, "principal", None)
    if not principal:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return principal


def get_limit_policy(request: Request) -> LimitPolicy:
    policy = getattr(request.state, "limit_policy", None)
    if not policy:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return policy


def has_role(actual_role: str, required_role: str) -> bool:
    return ROLE_LEVELS.get(actual_role, 0) >= ROLE_LEVELS.get(required_role, 0)


def require_role(required_role: str):
    required = _normalize_role(required_role)

    def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if not has_role(principal.role, required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required}' required",
            )
        return principal

    return dependency
