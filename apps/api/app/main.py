from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401  ensures all models are registered with Base.metadata
from app.core.config import get_settings
from app.core.database import init_db
from app.routers import admin, assessments, auth, candidates, interviews, jobs, matching, resumes, vira

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="VIRA API",
    description="Virtual Intelligent Recruitment Assistant -- Skills over background.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # In combined deployment, frontend and backend share an origin via nginx,
    # so CORS is only exercised in local dev (frontend on :3000, backend on :8000).
    allow_origins=[settings.frontend_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "ai_provider_mode": settings.ai_provider_mode}


@app.get("/api/health")
async def api_health():
    return {"status": "ok", "ai_provider_mode": settings.ai_provider_mode}


app.include_router(auth.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(matching.router, prefix="/api")
app.include_router(assessments.router, prefix="/api")
app.include_router(interviews.router, prefix="/api")
app.include_router(vira.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
