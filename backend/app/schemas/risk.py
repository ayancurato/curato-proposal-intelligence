"""
Curato Proposal Intelligence — Risk Schemas

Pydantic models for the Risk Engine output.
Every risk includes severity, explanation, and a suggested action.
"""

from __future__ import annotations

from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class RiskSeverity(str, Enum):
    """Risk severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    """Categories of risks identified in proposals."""
    MISSING_CLAUSE = "missing_clause"
    AMBIGUOUS_WORDING = "ambiguous_wording"
    HIDDEN_COST = "hidden_cost"
    WEAK_KPI = "weak_kpi"
    OWNERSHIP_ISSUE = "ownership_issue"
    REPORTING_GAP = "reporting_gap"
    TIMELINE_CONCERN = "timeline_concern"
    SCOPE_CREEP = "scope_creep"
    PAYMENT_RISK = "payment_risk"
    OTHER = "other"


class Risk(BaseModel):
    """A single identified risk in a proposal."""
    category: RiskCategory = Field(..., description="Type of risk")
    severity: RiskSeverity = Field(..., description="How critical is this risk")
    title: str = Field(..., description="Short risk title")
    explanation: str = Field(..., description="Detailed explanation of the risk")
    suggested_action: str = Field(..., description="What the founder should do about it")
    why_it_matters: Optional[str] = Field(None, description="Why this risk is important to address")
    business_impact: Optional[str] = Field(None, description="Potential business impact if ignored")
    affected_section: str = Field(
        "",
        description="Which part of the proposal this risk relates to",
    )


class ProposalRiskAnalysis(BaseModel):
    """Risk analysis for a single proposal."""
    proposal_id: str
    agency_name: str
    risks: list[Risk] = Field(default_factory=list)
    risk_score: float = Field(
        0.0,
        description="Overall risk score 0-100 (higher = riskier)",
    )
    summary: str = Field("", description="Executive summary of risks for this proposal")


class RiskAnalysisResult(BaseModel):
    """Combined risk analysis across all proposals in a session."""
    session_id: str
    analyses: list[ProposalRiskAnalysis] = Field(default_factory=list)
    comparative_insights: list[str] = Field(
        default_factory=list,
        description="Cross-proposal risk comparisons",
    )
