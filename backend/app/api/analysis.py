"""
Curato Proposal Intelligence — Analysis API Routes

Triggers and retrieves full proposal analysis pipeline results.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import get_settings
from app.schemas.dashboard import DashboardResponse
from app.schemas.session import SessionRead
from app.services.pipeline_service import PipelineService
from app.services.upload_service import UploadService

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post(
    "/{session_id}/start",
    response_model=SessionRead,
    summary="Start analysis pipeline",
    description="Triggers the full analysis pipeline for a session.",
)
async def start_analysis(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Start the analysis pipeline for a session.
    Runs asynchronously in the background. Poll the status endpoint
    to track progress.
    """
    settings = get_settings()
    upload_service = UploadService(db, settings)
    session = await upload_service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found.",
        )

    if session.status not in ("created", "failed"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Session is already in '{session.status}' state. Cannot restart.",
        )

    # ── Kick off pipeline in background ───────────────────────────
    background_tasks.add_task(
        PipelineService.run_pipeline,
        session_id=session_id,
        settings=settings,
    )

    # Update status to processing
    session.status = "processing"
    session.status_message = "Analysis pipeline started"
    await db.commit()

    return session


@router.get(
    "/{session_id}",
    response_model=DashboardResponse,
    summary="Get full analysis results",
    description="Returns the unified dashboard response with all analysis data.",
)
async def get_analysis(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the complete analysis results for a session.
    Returns the unified DashboardResponse with proposals, comparison,
    risk analysis, and recommendation.
    """
    pipeline_service = PipelineService(db, get_settings())
    dashboard = await pipeline_service.get_dashboard_response(session_id)

    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found.",
        )

    return dashboard


@router.get(
    "/{session_id}/status",
    response_model=SessionRead,
    summary="Get analysis pipeline status",
)
async def get_analysis_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the current status of the analysis pipeline."""
    upload_service = UploadService(db, get_settings())
    session = await upload_service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found.",
        )

    return session
