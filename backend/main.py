import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import router
from database.session import Base, engine
from services.settings import get_settings

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FirstAI Local Agent API", version="1.0.0")
request_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def rate_limit_for(path: str) -> int:
    if path.startswith("/api/agent"):
        return 30
    if path.startswith("/api/knowledge/upload"):
        return 20
    return 180


@app.middleware("http")
async def production_guardrails(request: Request, call_next):
    client = request.client.host if request.client else "unknown"
    key = f"{client}:{request.url.path}"
    now = time.monotonic()
    bucket = request_buckets[key]
    while bucket and bucket[0] < now - 60:
        bucket.popleft()
    if len(bucket) >= rate_limit_for(request.url.path):
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})
    bucket.append(now)

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=jsonable_encoder({"detail": exc.errors()}))


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

allowed_origins = {
    settings.frontend_origin,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

for origin in settings.allowed_origins.split(","):
    clean = origin.strip()
    if clean:
        allowed_origins.add(clean)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allowed_origins),
    allow_origin_regex=settings.allowed_origin_regex,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
