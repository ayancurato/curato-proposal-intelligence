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

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse

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


# ── Exception Handlers ────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if not errors:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "code": "VALIDATION_ERROR", "message": "Invalid request."},
        )
    
    first_error = errors[0]
    loc = first_error.get("loc", [])
    msg = first_error.get("msg", "")
    
    code = "VALIDATION_ERROR"
    user_msg = "Please check your inputs and try again."
    
    # Handle custom error format raised in validators
    if "Value error, " in msg:
        msg = msg.replace("Value error, ", "")
        
    if "|" in msg:
        parts = msg.split("|", 1)
        code = parts[0]
        user_msg = parts[1]
    else:
        # Fallback specific checks
        if loc and loc[-1] == "company_website":
            code = "INVALID_WEBSITE"
            user_msg = "Please enter a valid company website."
        elif loc and loc[-1] == "work_email":
            code = "PERSONAL_EMAIL_NOT_ALLOWED"
            user_msg = "Please enter a valid business email address to continue."
        else:
            user_msg = msg # Use Pydantic's default message or fallback

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "code": code, "message": user_msg},
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # If detail is already our custom dictionary format, return it as JSON
    if isinstance(exc.detail, dict) and "success" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
        
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "code": "ERROR", "message": str(exc.detail)},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[ERROR] Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "code": "SERVER_ERROR",
            "message": "Something went wrong. Please try again later."
        },
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
from app.api import upload, analysis, proposals, leads

app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(proposals.router)
app.include_router(leads.router)
