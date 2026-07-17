"""
Curato Proposal Intelligence — Recommendation Schemas

Pydantic models for the Recommendation Engine output.
No recommendation is returned without clear reasoning.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AgencyAssessment(BaseModel):
    """Assessment of a single agency's proposal."""
    agency_name: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    best_for: Optional[str] = Field(
        None,
        description="What type of founder/scenario this agency is best for",
    )
    overall_score: float = Field(
        0.0,
        description="Overall score 1-10",
    )


class TradeOff(BaseModel):
    """A trade-off between two agencies or approaches."""
    description: str = Field(..., description="What the trade-off is")
    agency_a: str = Field(..., description="First agency in the trade-off")
    agency_b: str = Field(..., description="Second agency in the trade-off")
    consideration: str = Field(
        ...,
        description="What the founder should consider when weighing this trade-off",
    )


class QuestionToAsk(BaseModel):
    """A question the founder should ask an agency before making a decision."""
    agency_name: str
    question: str
    why_it_matters: str = Field(..., description="Why this question is important")


class Recommendation(BaseModel):
    """
    The final recommendation output.
    Every recommendation includes clear reasoning — no unexplained outputs.
    """
    session_id: str

    # ── Best-Fit Agency ───────────────────────────────────────────
    best_fit_agency: str = Field(..., description="Name of the recommended agency")
    confidence_level: str = Field(
        ...,
        description="Confidence: high, medium, or low",
    )
    primary_reasoning: str = Field(
        ...,
        description="Main reason this agency is recommended",
    )
    detailed_reasoning: list[str] = Field(
        default_factory=list,
        description="Step-by-step reasoning chain",
    )

    # ── Per-Agency Assessment ─────────────────────────────────────
    assessments: list[AgencyAssessment] = Field(default_factory=list)

    # ── Trade-offs ────────────────────────────────────────────────
    trade_offs: list[TradeOff] = Field(default_factory=list)

    # ── Questions to Ask ──────────────────────────────────────────
    questions_to_ask: list[QuestionToAsk] = Field(default_factory=list)

    # ── Decision Framework ────────────────────────────────────────
    choose_agency_a_if: Optional[str] = Field(
        None,
        description="Choose the recommended agency if...",
    )
    choose_agency_b_if: Optional[str] = Field(
        None,
        description="Choose the runner-up agency if...",
    )

    # ── Executive Summary ─────────────────────────────────────────
    executive_summary: str = Field(
        "",
        description="One-paragraph summary of the recommendation for executives",
    )

    # ── Single Proposal Review Extras ─────────────────────────────
    proposal_readiness: Optional[str] = Field(
        None,
        description="Is this proposal ready to sign? (e.g., 'Ready', 'Needs Revision')",
    )
    things_to_clarify: list[str] = Field(
        default_factory=list,
        description="Items that need clarification before signing",
    )
    negotiation_suggestions: list[str] = Field(
        default_factory=list,
        description="Suggestions for negotiating better terms",
    )
