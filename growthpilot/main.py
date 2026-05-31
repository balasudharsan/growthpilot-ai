import os

from utils.config import load_project_env

load_project_env()

import asyncio
import time
from collections import defaultdict
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from database.db import init_db, save_input, save_report
from models.business_input import BusinessInput
from services.data_builder import build_business_payload
from services.llm_service import generate_strategy
from services.pdf_generator import generate_pdf
from services.report_builder import build_report
from services.template_engine import load_strategy_templates
from utils.logger import get_logger


logger = get_logger(__name__)
ANALYZE_RATE_LIMIT = os.getenv("RATE_LIMIT_ANALYZE", "5/minute")
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
STATIC_DIR = Path(__file__).parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"


class GlobalIPRateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 30, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._counts: dict = defaultdict(list)

    async def dispatch(self, request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window_seconds
        self._counts[ip] = [t for t in self._counts[ip] if t > window_start]
        if len(self._counts[ip]) >= self.max_requests:
            logger.warning(f"Global rate limit exceeded for IP: {ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests from this IP."}
            )
        self._counts[ip].append(now)
        return await call_next(request)


limiter = Limiter(key_func=get_remote_address, default_limits=[])

# Disable API docs in production for security
# Set ENVIRONMENT=production in .env to disable
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

app = FastAPI(
    title="GrowthPilot AI",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
    openapi_url="/openapi.json" if ENVIRONMENT == "development" else None,
)
app.state.limiter = limiter
app.add_middleware(GlobalIPRateLimiter, max_requests=30, window_seconds=60)
app.add_middleware(SlowAPIMiddleware)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    logger.warning("Rate limit exceeded")
    return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again later."})


@app.api_route("/health", methods=["GET", "HEAD"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root():
    return FileResponse(str(INDEX_FILE))


def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    expected_key = os.getenv("GROWTHPILOT_API_KEY")
    if not expected_key:
        logger.warning("GROWTHPILOT_API_KEY not set - endpoint is unprotected")
        return "unprotected"
    if api_key != expected_key:
        logger.warning(f"Invalid API key attempt: {api_key[:8] if api_key else 'none'}...")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key


@app.post("/analyze")
@limiter.limit(ANALYZE_RATE_LIMIT)
async def analyze(
    request: Request,
    business_input: BusinessInput,
    _: str = Depends(verify_api_key),
) -> dict:
    try:
        payload = build_business_payload(business_input)
        input_id = save_input(payload)
        templates = load_strategy_templates()
        strategy = await asyncio.to_thread(generate_strategy, payload)
        report = build_report(input_id, payload, strategy, templates)
        pdf_path = generate_pdf(report)
        save_report(input_id, report, pdf_path)
        return {
            "report_id": report["report_id"],
            "report": report,
            "pdf_path": pdf_path,
        }
    except Exception:
        logger.exception("Analyze request failed")
        raise HTTPException(status_code=500, detail="Unable to analyze business right now.")
