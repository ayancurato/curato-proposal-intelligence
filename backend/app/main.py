"""
Curato Proposal Intelligence -- FastAPI Application Entry Point

Configures CORS, lifespan events, and includes all API routers.
"""

import sys
import os

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — runs on startup and shutdown."""
    # ── Startup ───────────────────────────────────────────────────
    settings = get_settings()
    settings.upload_path  # Ensure upload directory exists
    await create_tables()
    print("[*] Curato Proposal Intelligence -- Server ready")
    yield
    # ── Shutdown ──────────────────────────────────────────────────
    print("[*] Curato Proposal Intelligence -- Server shutting down")


app = FastAPI(
    title="Curato Proposal Intelligence",
    description="AI-powered Decision Intelligence for marketing agency proposals",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────────────
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ──────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint to verify the server is running."""
    return {
        "status": "healthy",
        "service": "Curato Proposal Intelligence",
        "version": "1.0.0",
    }


# ── Include Routers ──────────────────────────────────────────────────
from app.api import upload, analysis, proposals

app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(proposals.router)
