export function getBackendUrl() {
  return (
    process.env.BACKEND_URL ||
    process.env.FASTAPI_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    'http://localhost:8000'
  )
}

export function withBackendAuth(headers: HeadersInit = {}) {
  const backendApiKey = process.env.BACKEND_API_KEY
  if (!backendApiKey) {
    return headers
  }

  const merged = new Headers(headers)
  merged.set('x-api-key', backendApiKey)
  return merged
}
