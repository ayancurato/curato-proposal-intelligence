"""
Curato Proposal Intelligence — Leads API Routes

Handles lead capture, validation, and session management.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, BackgroundTasks, Request, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.config import get_settings
from app.schemas.lead import LeadCreate, LeadResponse
from app.services.lead_service import LeadService

router = APIRouter(prefix="/api/leads", tags=["Leads"])


class ErrorResponse(BaseModel):
    success: bool
    message: str


class SessionResponse(BaseModel):
    valid: bool


@router.post(
    "",
    response_model=LeadResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Capture Lead",
)
async def capture_lead(
    lead: LeadCreate,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Validates and captures a new lead.
    Creates a secure session on success.
    """
    settings = get_settings()
    service = LeadService(db, settings)
    
    # Extract client IP and User-Agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        session_token = await service.process_lead(
            lead_data=lead,
            background_tasks=background_tasks,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except ValueError as e:
        # Expected business logic errors (e.g., Turnstile failure)
        response.status_code = 400
        return ErrorResponse(success=False, message=str(e))
    except Exception as e:
        print(f"[ERROR] Unexpected error in lead capture: {e}")
        response.status_code = 500
        return ErrorResponse(success=False, message="An unexpected error occurred.")

    # Calculate 30-day expiry for cookie
    expiry = datetime.now(timezone.utc) + timedelta(days=settings.session_expiry_days)
    
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_token,
        expires=expiry,
        httponly=True,
        secure=True,     # Must be served over HTTPS
        samesite="lax",
    )

    return LeadResponse(
        success=True,
        launch_url="https://www.curatointelligence.com"
    )


@router.get(
    "/session",
    response_model=SessionResponse,
    summary="Check Session",
)
async def check_session(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if the user has a valid secure session.
    """
    settings = get_settings()
    session_token = request.cookies.get(settings.session_cookie_name)
    
    if not session_token:
        return SessionResponse(valid=False)
        
    service = LeadService(db, settings)
    is_valid = await service.validate_session(session_token)
    
    return SessionResponse(valid=is_valid)
