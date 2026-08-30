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
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "ai_provider_mode": settings.ai_provider_mode}


app.include_router(auth.router)
app.include_router(candidates.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(assessments.router)
app.include_router(interviews.router)
app.include_router(vira.router)
app.include_router(admin.router)
