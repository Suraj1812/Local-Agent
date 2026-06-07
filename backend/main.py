from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from database.session import Base, engine
from services.settings import get_settings

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FirstAI Local Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
