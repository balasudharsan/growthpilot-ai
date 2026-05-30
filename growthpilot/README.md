# GrowthPilot AI

AI-powered business growth strategy system for small 
businesses, local shops, and service providers in 
Tier 2 and Tier 3 cities.

## What It Does
- Collects structured business information through an 
  8-step web form
- Analyses customer mindset, competition, pricing, 
  and marketing status using Groq LLM
- Generates a complete growth strategy report with 
  SWOT analysis, 30-day action plan, pricing strategy, 
  and WhatsApp marketing content
- Delivers results as a web report and downloadable PDF

## Target Users
Local shop owners, service providers, family businesses, 
new founders — anyone without access to a business 
consultant.

## Tech Stack
- Backend: FastAPI (Python)
- AI/LLM: Groq API (llama-3.3-70b-versatile)
- Database: PostgreSQL (production) / SQLite (local dev)
- PDF Generation: fpdf2
- Rate Limiting: SlowAPI + custom IP middleware
- Validation: Pydantic v2

## Architecture
10-layer modular pipeline:
1. Input Form / Web UI
2. Input Validation Layer (Pydantic v2)
3. Business Classification Layer
4. Data Cleaning and Structuring Layer
5. Strategy Workflow Engine
6. Knowledge / Template Layer
7. LLM Analysis Layer (Groq API)
8. Report Generation Layer
9. Database / Storage (PostgreSQL/SQLite)
10. PDF Output + Monitoring

## Security Features
- API key authentication on /analyze endpoint (X-API-Key)
- Prompt injection pattern detection and blocking
- Input sanitisation on all user text fields
- LLM output validation before storage
- Rate limiting: 5 valid requests/minute per IP
- Global IP rate limiting: 30 requests/minute (all traffic)
- Zero known CVEs (pip-audit clean)
- No sensitive data in logs
- All secrets in environment variables

## Local Setup

### Prerequisites
- Python 3.11+
- Groq API key (free at console.groq.com)

### Installation
git clone https://github.com/yourusername/growthpilot-ai
cd growthpilot_project
python -m venv growthpilot/.venv
growthpilot\.venv\Scripts\pip install -r growthpilot/requirements.txt

### Environment Variables
Copy growthpilot/.env.example to growthpilot/.env 
and fill in:
- GROQ_API_KEY — your Groq API key
- GROQ_MODEL — llama-3.3-70b-versatile
- GROWTHPILOT_API_KEY — any secret string for API auth
- RATE_LIMIT_ANALYZE — default: 5/minute
- DATABASE_URL — leave empty for SQLite locally

### Run
python -m uvicorn main:app --app-dir growthpilot 
  --host 127.0.0.1 --port 8000

Open http://127.0.0.1:8000

## API Usage
POST /analyze
Header: X-API-Key: your-api-key
Content-Type: application/json
Body: BusinessInput JSON (8 sections)

Returns: report with executive summary, SWOT, 
30-day action plan, pricing and marketing strategy

## Production Deployment
- Set DATABASE_URL to PostgreSQL connection string
- Set all env vars on server
- HTTPS required in production
- Debug mode must be OFF

## Known Limitations (MVP)
- SQLite in local dev — switch to PostgreSQL before deployment
- Rate limit counters reset on server restart (no Redis yet)
- PDF reports stored locally (move to S3/R2 before scaling)
- No user accounts or authentication per user

## Security Testing
Tested against:
- Prompt injection attacks
- Input fuzzing and oversized inputs
- Auth bypass attempts
- Rate limit abuse
- OWASP Top 10 checklist
- pip-audit: zero known vulnerabilities

## License
MIT
