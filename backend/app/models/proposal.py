"""
Curato Proposal Intelligence — Proposal Model

Represents a single uploaded proposal PDF and its extracted data.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ProposalStatus(str, enum.Enum):
    """Processing status of a single proposal."""
    UPLOADED = "uploaded"
    EXTRACTING_TEXT = "extracting_text"
    EXTRACTED_TEXT = "extracted_text"
    ANALYZING = "analyzing"
    EXTRACTED = "extracted"
    FAILED = "failed"


class Proposal(Base):
    """
    A single proposal PDF uploaded for analysis.
    Stores the file metadata, raw text, extracted structured data, and risk analysis.
    """
    __tablename__ = "proposals"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    # ── File Metadata ─────────────────────────────────────────────
    filename = Column(String(255), nullable=False)          # UUID-based stored name
    original_name = Column(String(255), nullable=False)     # User's original filename
    file_path = Column(String(500), nullable=False)         # Full path on disk
    file_size = Column(Integer, nullable=False)             # Size in bytes
    page_count = Column(Integer, nullable=True)             # Number of pages

    # ── Processing Status ─────────────────────────────────────────
    status = Column(
        SAEnum(ProposalStatus),
        nullable=False,
        default=ProposalStatus.UPLOADED,
    )
    error_message = Column(String(1000), nullable=True)

    # ── Content ───────────────────────────────────────────────────
    raw_text = Column(Text, nullable=True)                  # Extracted PDF text
    extracted_data = Column(Text, nullable=True)            # Structured JSON from AI
    risks = Column(Text, nullable=True)                     # Risk analysis JSON

    # ── Session Reference ─────────────────────────────────────────
    session_id = Column(
        String(36),
        ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

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
    session = relationship("AnalysisSession", back_populates="proposals")

    def __repr__(self) -> str:
        return f"<Proposal id={self.id} name={self.original_name} status={self.status}>"
