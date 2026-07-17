"""
Curato Proposal Intelligence — Proposals API Routes

CRUD operations for individual proposals within a session.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Proposal
from app.schemas.proposal import ProposalRead

router = APIRouter(prefix="/api/proposals", tags=["Proposals"])


@router.get(
    "/session/{session_id}",
    response_model=list[ProposalRead],
    summary="Get all proposals in a session",
)
async def get_session_proposals(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all proposals belonging to an analysis session."""
    result = await db.execute(
        select(Proposal).where(Proposal.session_id == session_id)
    )
    proposals = result.scalars().all()

    if not proposals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No proposals found for session {session_id}.",
        )

    return proposals


@router.get(
    "/{proposal_id}",
    response_model=ProposalRead,
    summary="Get a single proposal",
)
async def get_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a single proposal."""
    result = await db.execute(
        select(Proposal).where(Proposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal {proposal_id} not found.",
        )

    return proposal
