"""
Curato Proposal Intelligence — Proposal Schemas

Pydantic models for proposal data: API request/response shapes and
the structured extraction schema that the AI engine must produce.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Status Enum ──────────────────────────────────────────────────────
class ProposalStatusEnum(str, Enum):
    UPLOADED = "uploaded"
    EXTRACTING_TEXT = "extracting_text"
    EXTRACTED_TEXT = "extracted_text"
    ANALYZING = "analyzing"
    EXTRACTED = "extracted"
    FAILED = "failed"


# ═══════════════════════════════════════════════════════════════════════
# EXTRACTED PROPOSAL — The structured JSON the AI engine must return
# ═══════════════════════════════════════════════════════════════════════

class ContactInfo(BaseModel):
    """Agency contact information."""
    name: Optional[str] = Field(None, description="Primary contact name")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")
    role: Optional[str] = Field(None, description="Contact role/title")


class PricingItem(BaseModel):
    """Individual line item in the pricing breakdown."""
    item: str = Field(..., description="Name of the deliverable or service")
    amount: Optional[float] = Field(None, description="Cost in USD")
    description: Optional[str] = Field(None, description="Additional pricing details")


class Pricing(BaseModel):
    """Complete pricing structure of the proposal."""
    total_cost: Optional[float] = Field(None, description="Total project cost in USD")
    currency: str = Field("USD", description="Currency code")
    breakdown: list[PricingItem] = Field(default_factory=list, description="Itemized pricing")
    payment_terms: Optional[str] = Field(None, description="Payment schedule and terms")
    retainer_fee: Optional[float] = Field(None, description="Monthly retainer if applicable")
    setup_fee: Optional[float] = Field(None, description="One-time setup fee if applicable")
    pricing_model: Optional[str] = Field(
        None,
        description="Pricing model: fixed, hourly, retainer, performance-based, hybrid",
    )

    @field_validator("breakdown", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        return v if v is not None else []


class Milestone(BaseModel):
    """A milestone within the project timeline."""
    name: str = Field(..., description="Milestone name")
    target_date: Optional[str] = Field(None, description="Target completion date")
    deliverables: list[str] = Field(default_factory=list, description="What is delivered at this milestone")

    @field_validator("deliverables", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        return v if v is not None else []


class Timeline(BaseModel):
    """Project timeline with milestones."""
    start_date: Optional[str] = Field(None, description="Project start date")
    end_date: Optional[str] = Field(None, description="Project end date")
    duration: Optional[str] = Field(None, description="Total duration (e.g., '3 months')")
    milestones: list[Milestone] = Field(default_factory=list, description="Project milestones")

    @field_validator("milestones", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        return v if v is not None else []


class TeamMember(BaseModel):
    """A member of the proposed team."""
    name: Optional[str] = Field(None, description="Team member name")
    role: str = Field(..., description="Role on the project")
    experience: Optional[str] = Field(None, description="Relevant experience")


class Team(BaseModel):
    """Proposed team structure."""
    total_members: Optional[int] = Field(None, description="Total team size")
    members: list[TeamMember] = Field(default_factory=list, description="Individual team members")
    structure: Optional[str] = Field(None, description="Team structure description")

    @field_validator("members", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        return v if v is not None else []


class KPI(BaseModel):
    """Key Performance Indicator proposed by the agency."""
    metric: str = Field(..., description="KPI metric name")
    target: Optional[str] = Field(None, description="Target value or range")
    measurement_method: Optional[str] = Field(None, description="How this KPI will be measured")


class Reporting(BaseModel):
    """Reporting structure proposed by the agency."""
    frequency: Optional[str] = Field(None, description="Reporting frequency (weekly, monthly, etc.)")
    format: Optional[str] = Field(None, description="Report format")
    metrics_included: list[str] = Field(default_factory=list, description="Metrics included in reports")
    tools: list[str] = Field(default_factory=list, description="Tools used for reporting")

    @field_validator("metrics_included", "tools", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        return v if v is not None else []


class Deliverable(BaseModel):
    """A specific deliverable in the proposal."""
    name: str = Field(..., description="Deliverable name")
    description: Optional[str] = Field(None, description="Detailed description")
    timeline: Optional[str] = Field(None, description="When this will be delivered")


class ExtractedProposal(BaseModel):
    """
    The complete structured representation of a marketing agency proposal.
    This is the canonical schema that the AI extraction engine must produce.
    """
    agency_name: str = Field(..., description="Name of the agency")
    contact_info: Optional[ContactInfo] = Field(None, description="Agency contact details")
    executive_summary: Optional[str] = Field(None, description="High-level proposal summary")

    # ── Core Business Dimensions ──────────────────────────────────
    pricing: Pricing = Field(default_factory=Pricing, description="Pricing details")
    deliverables: list[Deliverable] = Field(default_factory=list, description="List of deliverables")
    timeline: Timeline = Field(default_factory=Timeline, description="Project timeline")
    team: Team = Field(default_factory=Team, description="Proposed team")
    scope: Optional[str] = Field(None, description="Project scope description")
    kpis: list[KPI] = Field(default_factory=list, description="Proposed KPIs")
    reporting: Reporting = Field(default_factory=Reporting, description="Reporting structure")

    # ── Legal & Terms ─────────────────────────────────────────────
    ownership_terms: Optional[str] = Field(None, description="IP and asset ownership terms")
    termination_clause: Optional[str] = Field(None, description="Contract termination terms")
    confidentiality_terms: Optional[str] = Field(None, description="NDA or confidentiality terms")
    additional_terms: Optional[str] = Field(None, description="Other notable terms")

    # ── Meta ──────────────────────────────────────────────────────
    unique_selling_points: list[str] = Field(
        default_factory=list,
        description="What makes this agency/proposal stand out",
    )
    case_studies: list[str] = Field(
        default_factory=list,
        description="Referenced case studies or past work",
    )

    @field_validator("deliverables", "kpis", "unique_selling_points", "case_studies", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        return v if v is not None else []


# ═══════════════════════════════════════════════════════════════════════
# API RESPONSE SCHEMAS
# ═══════════════════════════════════════════════════════════════════════

class ProposalRead(BaseModel):
    """API response schema for a proposal."""
    id: str
    filename: str
    original_name: str
    file_size: int
    page_count: Optional[int] = None
    status: ProposalStatusEnum
    error_message: Optional[str] = None
    extracted_data: Optional[ExtractedProposal] = None
    session_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProposalSummary(BaseModel):
    """Lightweight proposal summary for list views."""
    id: str
    original_name: str
    status: ProposalStatusEnum
    agency_name: Optional[str] = None
    total_cost: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}
