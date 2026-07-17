"""
Curato Proposal Intelligence — Upload API Routes

Handles PDF file uploads and session creation.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import get_settings
from app.services.upload_service import UploadService
from app.schemas.session import SessionRead

router = APIRouter(prefix="/api/upload", tags=["Upload"])


@router.post(
    "",
    response_model=SessionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload proposal PDFs",
    description="Upload one or more marketing agency proposal PDFs for analysis.",
)
async def upload_proposals(
    files: list[UploadFile] = File(..., description="PDF files to upload"),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload multiple PDF proposal files. Creates an analysis session
    and returns the session with uploaded proposal metadata.
    """
    settings = get_settings()

    # ── Validation ────────────────────────────────────────────────
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one PDF file is required.",
        )

    if len(files) > settings.max_proposals_per_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.max_proposals_per_session} proposals per session.",
        )

    # ── Process Upload ────────────────────────────────────────────
    upload_service = UploadService(db, settings)
    session = await upload_service.handle_upload(files)

    return session


@router.get(
    "/{session_id}/status",
    response_model=SessionRead,
    summary="Get upload session status",
)
async def get_session_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the current status of an analysis session."""
    upload_service = UploadService(db, get_settings())
    session = await upload_service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found.",
        )

    return session
