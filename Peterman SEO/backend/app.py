"""
Genie v2.1 — The AI Bookkeeper
Almost Magic Finance Suite — Agent 01

Backend API server (FastAPI + SQLite + SQLCipher)
"""

import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Peterman routes
from routes.health import router as health_router
from routes.dashboard import router as dashboard_router
from routes.brands import router as brands_router
from routes.perception import router as perception_router
from routes.semantic import router as semantic_router
from routes.vectormap import router as vectormap_router
from routes.authority import router as authority_router
from routes.survivability import router as survivability_router
from routes.machine import router as machine_router
from routes.amplifier import router as amplifier_router
from routes.proof import router as proof_router
from routes.oracle import router as oracle_router
from routes.forge import router as forge_router
from routes.seo_ask import router as seo_ask_router
from routes.browser import router as browser_router
from routes.settings import router as settings_router
from models.database import init_db, get_db_path

# ── App Setup ──────────────────────────────────────────────
app = FastAPI(
    title="Peterman V4.1 — The Authority & Presence Engine",
    description="Almost Magic Tech Lab. AI-era brand visibility, LLM ranking, and SEO optimisation.",
    version="4.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "file://"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Routes ───────────────────────────────────────────
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(brands_router, prefix="/api/brands", tags=["Brands"])
app.include_router(perception_router, prefix="/api/scan/perception", tags=["Perception"])
app.include_router(semantic_router, prefix="/api/semantic", tags=["Semantic Core"])
app.include_router(vectormap_router, prefix="/api/vectormap", tags=["Vector Map"])
app.include_router(authority_router, prefix="/api/authority", tags=["Authority Engine"])
app.include_router(survivability_router, prefix="/api/survivability", tags=["Survivability Lab"])
app.include_router(machine_router, prefix="/api/technical", tags=["Machine Interface"])
app.include_router(amplifier_router, prefix="/api/amplifier", tags=["Amplifier"])
app.include_router(proof_router, prefix="/api/proof", tags=["The Proof"])
app.include_router(oracle_router, prefix="/api/oracle", tags=["The Oracle"])
app.include_router(forge_router, prefix="/api/forge", tags=["The Forge"])
app.include_router(seo_ask_router, prefix="/api/seo", tags=["SEO Ask"])
app.include_router(browser_router, prefix="/api/browser", tags=["Browser LLMs"])
app.include_router(settings_router, prefix="/api/settings", tags=["Settings"])


# ── Status (No duplicate - handled by routes/health.py) ───────────────────────


# ── Startup ────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    """Initialise database on startup."""
    init_db()
    print("🎭 Peterman V4.1 — The Authority & Presence Engine")
    print(f"   Database: {get_db_path()}")
    print(f"   API docs: http://localhost:5008/api/docs")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5008, reload=True)
