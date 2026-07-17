"""
Curato Proposal Intelligence — AnalysisSession Model

Represents a group of proposals uploaded together for comparison.
One session contains multiple proposals and their combined analysis results.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class SessionStatus(str, enum.Enum):
    """Status of an analysis session."""
    CREATED = "created"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    EXTRACTING = "extracting"
    COMPARING = "comparing"
    ANALYZING_RISKS = "analyzing_risks"
    RECOMMENDING = "recommending"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisSession(Base):
    """
    An analysis session groups multiple proposals for comparison.
    Stores the combined comparison, risk, and recommendation results.
    """
    __tablename__ = "analysis_sessions"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    status = Column(
        SAEnum(SessionStatus),
        nullable=False,
        default=SessionStatus.CREATED,
    )
    status_message = Column(String(500), nullable=True)

    # ── Combined Analysis Results (stored as JSON strings) ────────
    comparison_data = Column(Text, nullable=True)
    recommendation_data = Column(Text, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ─────────────────────────────────────────────
    proposals = relationship(
        "Proposal",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AnalysisSession id={self.id} status={self.status}>"
