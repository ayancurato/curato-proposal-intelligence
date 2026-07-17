"""
Curato Proposal Intelligence — Dashboard Schemas

Unified response schema that combines all module outputs into a single
frontend-friendly API response. The frontend should never need to
perform business logic — everything is pre-computed here.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.proposal import ProposalRead
from app.schemas.comparison import ComparisonResult
from app.schemas.risk import RiskAnalysisResult
from app.schemas.recommendation import Recommendation
from app.schemas.session import SessionStatusEnum


class DashboardResponse(BaseModel):
    """
    The unified response that powers the entire frontend dashboard.
    Combines outputs from all modules into one payload.
    """
    session_id: str
    status: SessionStatusEnum
    status_message: Optional[str] = None

    # ── Proposals ─────────────────────────────────────────────────
    proposals: list[ProposalRead] = Field(default_factory=list)
    proposal_count: int = 0

    # ── Comparison ────────────────────────────────────────────────
    comparison: Optional[ComparisonResult] = None

    # ── Risk Analysis ─────────────────────────────────────────────
    risk_analysis: Optional[RiskAnalysisResult] = None

    # ── Recommendation ────────────────────────────────────────────
    recommendation: Optional[Recommendation] = None

    # ── Quick Stats (precomputed for dashboard cards) ─────────────
    quick_stats: Optional[QuickStats] = None


class QuickStats(BaseModel):
    """Pre-computed statistics for the dashboard overview cards."""
    total_proposals: int = 0
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    avg_timeline_days: Optional[int] = None
    total_risks: int = 0
    critical_risks: int = 0
    high_risks: int = 0
    recommended_agency: Optional[str] = None
    confidence_level: Optional[str] = None
    health_score: Optional[float] = None


# Fix forward reference — QuickStats is used in DashboardResponse above
DashboardResponse.model_rebuild()
