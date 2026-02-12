"""KnowYourself — FastAPI application.

Personality assessment and self-discovery tool for the AMTL Ground Series.
Port: 8300
"""

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models import Base
from app.routers import assessments, history, journal, questions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("KnowYourself v%s starting on port %s", settings.app_version, settings.app_port)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")
    yield
    await engine.dispose()
    logger.info("KnowYourself shut down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting bypass for tests
if os.environ.get("KNOWYOURSELF_TESTING") == "1":
    logger.info("Testing mode: rate limiting bypassed")

# Routers
app.include_router(assessments.router)
app.include_router(journal.router)
app.include_router(history.router)
app.include_router(questions.router)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "knowyourself",
        "version": settings.app_version,
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    if duration > 1.0:
        logger.info("%s %s %.2fs", request.method, request.url.path, duration)
    return response
