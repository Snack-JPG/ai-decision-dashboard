# AI Decision Support Dashboard

**Purpose:** Portfolio project demonstrating AI-powered data intelligence for government/enterprise use cases. Built to complement Change Radar (enterprise SaaS) and LexFlow (agentic AI) in a job application for an AI Software Engineer role at a UK government consultancy.

## What It Does

Upload structured CSV data (or connect to public APIs in a future iteration), and the system:
1. Auto-detects schema and data types
2. Runs AI analysis — trends, anomalies, seasonal patterns, correlations
3. Generates natural language insights with confidence scores
4. Lets you ask questions in plain English ("What caused the Q3 spike?")
5. Produces a formatted briefing document (PDF/Markdown)

## Demo Dataset

**UK NHS A&E Waiting Times** (from NHS England stats)
- Monthly data by trust/region
- Metrics: attendances, 4-hour target performance, admissions, breaches
- Real, messy, government data — perfect for the portfolio story

Also support arbitrary CSV upload so reviewers can try their own data.

## Tech Stack

| Layer | Tech | Why |
|-------|------|-----|
| Frontend | Next.js 15, TypeScript, Tailwind CSS | Fast, modern, shows TypeScript skills |
| Charts | Recharts | Clean, React-native charting |
| UI Components | shadcn/ui | Professional look, minimal effort |
| AI Backend | Python (FastAPI) | Shows Python proficiency (role requires it) |
| AI Model | Anthropic Claude via API | Analysis, NL queries, briefing generation |
| Database | SQLite (via SQLAlchemy) | Zero config, portable, no external deps |
| Deploy | Vercel (frontend) + Railway (Python) | Free tier, instant deploy |

## Architecture

```
┌─────────────────────────────────────────────┐
│                 Next.js Frontend             │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │ Upload & │  │Dashboard │  │  Query    │ │
│  │ Ingest   │  │& Charts  │  │  Interface│ │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘ │
│       │              │              │       │
│       └──────────────┼──────────────┘       │
│                      │                      │
│              ┌───────┴────────┐             │
│              │  API Routes    │             │
│              └───────┬────────┘             │
└──────────────────────┼──────────────────────┘
                       │
              ┌────────┴────────┐
              │  FastAPI Backend │
              │                 │
              │  ┌────────────┐ │
              │  │ Ingestion  │ │
              │  │ Engine     │ │
              │  ├────────────┤ │
              │  │ Analysis   │ │
              │  │ Engine     │ │
              │  ├────────────┤ │
              │  │ NL Query   │ │
              │  │ Engine     │ │
              │  ├────────────┤ │
              │  │ Briefing   │ │
              │  │ Generator  │ │
              │  └────────────┘ │
              │                 │
              │  SQLite + Claude│
              └─────────────────┘
```

## Features

### 1. Data Ingestion
- Drag-and-drop CSV upload
- Auto-detect column types (date, numeric, categorical, text)
- Schema preview with suggested column roles (metric vs dimension vs time)
- Data quality check (missing values, outliers, format issues)
- Store parsed data in SQLite for querying

### 2. Dashboard
- **Overview cards** — key metrics with sparklines, trend arrows, % change
- **Time series chart** — main metric over time, with anomaly markers
- **Comparison view** — side-by-side metrics, normalised or absolute
- **Breakdown table** — drill into dimensions (e.g., by region, by category)
- **Anomaly highlights** — flagged data points with AI explanations
- All charts interactive — click to drill down, hover for details

### 3. AI Analysis Engine (Python)
- **Trend detection** — linear regression, moving averages, direction changes
- **Anomaly detection** — Z-score based + IQR method, contextual anomalies
- **Seasonal decomposition** — identify recurring patterns
- **Correlation finder** — which metrics move together
- **Change point detection** — when did the trend shift
- Each finding includes:
  - Natural language explanation
  - Confidence score (0-1)
  - Supporting data points
  - Suggested action

### 4. Natural Language Query
- Chat interface: "Why did waiting times spike in December?"
- AI has full context of the dataset + pre-computed analysis
- Answers cite specific data points
- Follow-up questions maintain context
- Suggested questions based on the data

### 5. Briefing Generator
- One-click "Generate Briefing" button
- Produces structured report:
  - Executive Summary (3-4 sentences)
  - Key Findings (top 5, ranked by importance)
  - Anomalies & Risks
  - Trend Analysis
  - Recommendations
- Export as Markdown or PDF
- Tone: professional, suitable for government stakeholders

### 6. Confidence & Transparency
- Every AI insight has a confidence score badge
- "Show reasoning" expandable for each insight
- Data lineage — click any number to see the source rows
- No black box — full transparency on how conclusions were reached

### 7. Production Readiness
- API-key authentication with role-based access control (viewer/analyst/admin)
- Per-client request rate limiting and daily quotas (requests/upload bytes/analysis jobs)
- Asynchronous analysis job queue with job-status polling
- Metrics endpoint and alert-webhook hooks for operational visibility

## Pages

1. **/** — Landing/upload page. Hero + drag-drop area + demo data button
2. **/dashboard/[id]** — Main dashboard for a dataset
3. **/dashboard/[id]/query** — NL query interface (or as a slide-over panel)
4. **/dashboard/[id]/briefing** — Generated briefing view + export

## API Routes (Next.js → FastAPI)

### Next.js API Routes (proxy to FastAPI)
- `POST /api/upload` — Handle file upload, store raw data
- `GET /api/datasets` — List uploaded datasets
- `GET /api/datasets/[id]` — Get dataset metadata + summary

### FastAPI Endpoints
- `POST /ingest` — Parse CSV/JSON, detect schema, store in SQLite
- `POST /analyze` — Run full analysis pipeline on a dataset
- `GET /analyze/[id]/results` — Get cached analysis results
- `POST /query` — Natural language query against a dataset
- `POST /briefing` — Generate briefing document
- `GET /health` — Health check

## Design

- **Dark mode default** (light mode toggle) — modern, professional
- **Minimal chrome** — let the data breathe
- **Color palette:** Blue-gray base, amber for warnings/anomalies, green for positive trends, red for negative
- **Typography:** Inter or Geist Sans
- **Cards with subtle borders** — not heavy shadows
- **Responsive** but desktop-first (this is a professional tool)

## Demo Flow (for portfolio)

1. Visitor lands on homepage, sees clean hero: "AI-powered decision intelligence for public sector data"
2. Click "Try Demo" → loads NHS A&E data automatically
3. Dashboard populates with charts, anomaly markers, insight cards
4. Try the query box: "Which trusts are consistently missing the 4-hour target?"
5. Click "Generate Briefing" → professional report appears
6. Impressed. Clicks GitHub link. Sees clean code.

## MVP Scope (Weekend Build)

**In scope:**
- CSV upload + auto-schema detection
- Dashboard with time series + overview cards + anomaly markers
- AI analysis (trends, anomalies, key insights)
- NL query interface
- Briefing generator
- NHS demo dataset pre-loaded
- Deployed and live

**Out of scope (future):**
- User accounts / auth
- Multiple datasets simultaneously
- Real-time data connections (API polling)
- Collaborative features
- Export to PowerPoint
