"""
Curato Proposal Intelligence — Session Schemas

Pydantic models for analysis session API request/response shapes.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.proposal import ProposalSummary


class SessionStatusEnum(str, Enum):
    CREATED = "created"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    EXTRACTING = "extracting"
    COMPARING = "comparing"
    ANALYZING_RISKS = "analyzing_risks"
    RECOMMENDING = "recommending"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionCreate(BaseModel):
    """Input schema for creating a new analysis session."""
    pass  # Created implicitly during upload


class SessionRead(BaseModel):
    """API response schema for an analysis session."""
    id: str
    status: SessionStatusEnum
    status_message: Optional[str] = None
    proposal_count: int = 0
    proposals: list[ProposalSummary] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
