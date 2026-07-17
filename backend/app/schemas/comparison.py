"""
Curato Proposal Intelligence — Comparison Schemas

Pydantic models for the structured output of the Comparison Engine.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class DimensionScore(BaseModel):
    """Score and analysis for a single comparison dimension."""
    dimension: str = Field(..., description="Name of the comparison dimension")
    scores: dict[str, Optional[float]] = Field(
        ...,
        description="Agency name → score (1-10) mapping. Value is null if information is missing.",
    )
    leader: Optional[str] = Field(None, description="Agency that leads in this dimension")
    analysis: str = Field(..., description="AI reasoning for the scores in this dimension")
    key_differences: list[str] = Field(
        default_factory=list,
        description="Notable differences between proposals in this dimension",
    )


class PricingComparison(BaseModel):
    """Detailed pricing comparison across proposals."""
    lowest_cost_agency: Optional[str] = None
    highest_cost_agency: Optional[str] = None
    price_range: Optional[str] = Field(None, description="e.g., '$10,000 - $25,000'")
    best_value_agency: Optional[str] = Field(None, description="Best value considering scope")
    value_reasoning: Optional[str] = None
    pricing_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Agency name → total cost",
    )


class ComparisonResult(BaseModel):
    """
    Complete comparison output across all business dimensions.
    This is the canonical schema for the Comparison Engine output.
    """
    session_id: str
    proposal_count: int
    agency_names: list[str] = Field(default_factory=list)

    # ── Per-Dimension Analysis ────────────────────────────────────
    dimensions: list[DimensionScore] = Field(
        default_factory=list,
        description="Scored comparison across all dimensions",
    )

    # ── Pricing Deep-Dive ─────────────────────────────────────────
    pricing_comparison: PricingComparison = Field(
        default_factory=PricingComparison,
    )

    # ── Overall Summary ───────────────────────────────────────────
    overall_summary: str = Field(
        "",
        description="Executive summary of the comparison across all dimensions",
    )
    head_to_head: list[str] = Field(
        default_factory=list,
        description="Key head-to-head insights",
    )
