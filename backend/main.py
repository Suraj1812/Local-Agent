from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from database.session import Base, engine
from services.settings import get_settings

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FirstAI Local Agent API", version="1.0.0")

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
