# AI Decision Support Dashboard

An AI-powered data intelligence platform for government and enterprise use cases. Upload datasets, get instant AI insights, and generate briefing documents.

![Screenshot](./docs/screenshot-placeholder.png)
*Screenshot coming soon - dashboard with charts and AI insights*

## What it does

- **Smart Data Analysis**: Upload CSV files and get automated statistical analysis with trend detection, anomaly spotting, and pattern recognition
- **Natural Language Queries**: Ask questions in plain English like "What caused the Q3 spike?" and get AI-generated explanations
- **Interactive Dashboard**: Modern React-based UI with responsive charts and real-time data visualization
- **Executive Briefings**: Generate formatted reports with key insights, trends, and actionable recommendations
- **Production Guardrails**: API-key auth/RBAC, per-client rate limits + daily quotas, async analysis job queue, and metrics/alert hooks
- **NHS Demo Dataset**: Pre-loaded with real UK NHS A&E waiting times data for demonstration

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Next.js 15, TypeScript | Modern React framework with SSR |
| UI Components | shadcn/ui, Tailwind CSS | Professional design system |
| Charts | Recharts | Interactive data visualization |
| Backend API | Python FastAPI | High-performance async API |
| AI Engine | Anthropic Claude | Natural language analysis |
| Database | SQLite | Zero-config data persistence |
| Deployment | Vercel + Railway | Scalable hosting |

## Architecture

```
┌─────────────────────────────────────────────┐
│                Next.js Frontend              │
│  ┌─────────┐ ┌─────────┐ ┌──────────────┐   │
│  │ Upload  │ │Dashboard│ │    Query     │   │
│  │   UI    │ │& Charts │ │  Interface   │   │
│  └─────────┘ └─────────┘ └──────────────┘   │
└──────────────────┬──────────────────────────┘
                   │ HTTP/REST API
┌─────────────────────────────────────────────┐
│              FastAPI Backend                │
│  ┌─────────┐ ┌─────────┐ ┌──────────────┐   │
│  │ Data    │ │ AI      │ │   Analysis   │   │
│  │Ingestion│ │Engine   │ │   Service    │   │
│  └─────────┘ └─────────┘ └──────────────┘   │
└─────────────────┬───────────────────────────┘
                  │ ORM
        ┌─────────────────┐
        │  SQLite Database │
        └─────────────────┘
```

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Anthropic API key

### Frontend Setup
```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
# Edit .env.local and add your backend URL if different from localhost:8000

# Start development server
npm run dev
```

### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Initialize database
python run.py init-db

# Start the API server
python run.py
```

### Environment Variables

**Frontend (.env.local):**
```
BACKEND_URL=http://localhost:8000
```

**Backend (.env):**
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
AUTH_ENABLED=false
API_KEYS_JSON=[{"key":"admin-key","client_id":"admin","role":"admin"}]
ALERT_WEBHOOK_URL=
CORS_ORIGINS=http://localhost:3000
```

Optional: set `BACKEND_API_KEY` in `.env.local` so Next.js API routes authenticate to FastAPI when `AUTH_ENABLED=true`.

## Testing

```bash
# Frontend checks
npm run lint
npm run build

# Backend workflow/security checks
python3 backend/test_analysis.py
python3 backend/test_e2e.py
python3 backend/test_security.py
```

## Demo

The dashboard comes pre-loaded with real **NHS A&E waiting times** data from NHS England:
- Monthly attendance figures by trust and region
- 4-hour target performance metrics
- Admission rates and breach statistics
- Covers multiple regions across England

This demonstrates the platform's ability to handle real government data with all its inherent complexity and messiness - perfect for showcasing practical AI analysis capabilities.

## Deployment

### Frontend (Vercel)

1. Fork this repository
2. Connect to Vercel via GitHub
3. Set environment variable: `BACKEND_URL` to your Railway backend URL
4. Deploy automatically

### Backend (Railway)

1. Create new Railway project
2. Connect to GitHub and select the `backend` folder
3. Add environment variable: `ANTHROPIC_API_KEY`
4. Railway will auto-detect Python and use the Procfile
5. Copy the generated Railway URL for frontend config

### Environment Variables for Production

**Vercel Frontend:**
```
BACKEND_URL=https://your-railway-backend.railway.app
```

**Railway Backend:**
```
ANTHROPIC_API_KEY=sk-ant-...
API_HOST=0.0.0.0
```

## Built by

**Austin Mander**  
[austinmander04@gmail.com](mailto:austinmander04@gmail.com)

*Created as a portfolio project demonstrating AI-powered data intelligence for enterprise and government applications.*
