"""
Curato Proposal Intelligence — Schemas Package

Re-exports all Pydantic schemas for convenient imports.
"""

from app.schemas.proposal import (
    ExtractedProposal,
    ProposalRead,
    ProposalSummary,
    ProposalStatusEnum,
    ContactInfo,
    Pricing,
    PricingItem,
    Timeline,
    Milestone,
    Team,
    TeamMember,
    KPI,
    Reporting,
    Deliverable,
)
from app.schemas.session import SessionRead, SessionStatusEnum
from app.schemas.comparison import ComparisonResult, DimensionScore, PricingComparison
from app.schemas.risk import (
    Risk,
    RiskSeverity,
    RiskCategory,
    ProposalRiskAnalysis,
    RiskAnalysisResult,
)
from app.schemas.recommendation import (
    Recommendation,
    AgencyAssessment,
    TradeOff,
    QuestionToAsk,
)
from app.schemas.dashboard import DashboardResponse, QuickStats

__all__ = [
    "ExtractedProposal",
    "ProposalRead",
    "ProposalSummary",
    "ProposalStatusEnum",
    "ContactInfo",
    "Pricing",
    "PricingItem",
    "Timeline",
    "Milestone",
    "Team",
    "TeamMember",
    "KPI",
    "Reporting",
    "Deliverable",
    "SessionRead",
    "SessionStatusEnum",
    "ComparisonResult",
    "DimensionScore",
    "PricingComparison",
    "Risk",
    "RiskSeverity",
    "RiskCategory",
    "ProposalRiskAnalysis",
    "RiskAnalysisResult",
    "Recommendation",
    "AgencyAssessment",
    "TradeOff",
    "QuestionToAsk",
    "DashboardResponse",
    "QuickStats",
]
