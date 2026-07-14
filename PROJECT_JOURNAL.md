# GrowthPilot AI

An AI-powered business growth strategy tool for small business owners. Answer 8 simple questions → receive a SWOT analysis, 30-day action plan, pricing strategy, WhatsApp marketing content, and a downloadable PDF report — all in under 2 minutes.

🔗 **Live:** https://growthpilot-ai-2bai.onrender.com/

---

## Why I built this

Small business owners in India often run on instinct because professional consultants are expensive. I wanted to see if AI could provide a structured starting point — not replace a consultant, but offer real guidance to people who would otherwise have none.

## What makes this different

This is not a generic LLM wrapper. It is built with security designed in from the architecture stage, not added afterward.

**10-layer architecture:**
1. Input Validation (Pydantic v2)
2. Authentication (X-API-Key header)
3. Sanitisation (regex-based prompt injection blocking)
4. Classification (Python logic)
5. Data Structuring
6. Template Engine (per business type)
7. LLM Analysis (Groq, llama-3.3-70b-versatile)
8. Output Validation (Pydantic on LLM response)
9. Report Builder (LLM + templates merged)
10. PDF Generator (fpdf2)

**Security features:**
- API key authentication on protected endpoints
- Two-layer rate limiting (endpoint + global middleware)
- Prompt injection regex blocking before any LLM call
- LLM output schema validation with safe fallback
- 30s timeout + 3-attempt exponential backoff on LLM calls
- Async event loop handling (`asyncio.to_thread()` for blocking ops)
- Bandit code security scan: 0 issues
- pip-audit dependency scan: 0 known CVEs
- Swagger docs hidden in production
- Environment variables for all secrets

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.12) |
| LLM | Groq API |
| Database | PostgreSQL (Supabase) |
| PDF | fpdf2 |
| Hosting | OnRender |
| Monitoring | UptimeRobot |

## Local setup

```bash
git clone https://github.com/balasudharsan/growthpilot-ai.git
cd growthpilot-ai
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
cp .env.example .env       # add your keys
python -m uvicorn main:app --app-dir growthpilot --port 8000
```

Then visit `http://127.0.0.1:8000`

## Documentation

- [Project Journal](./PROJECT_JOURNAL.md) — Full build log: every decision, every error, every fix.
- [Architecture Notes](./docs/architecture.md)
- [Security Notes](./docs/security.md)
- [API Documentation](./docs/api.md)

## Honest note

I am self-taught and early in my career. This is my first production AI project. I built it carefully because I believe AI tools should clear a higher bar — useful, structured, and secure. Feedback welcome.

## License

MIT
