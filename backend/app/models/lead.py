"""
Curato Proposal Intelligence — Lead Model

Database model for captured leads across all Curato AI tools.
"""

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, DateTime

from app.database import Base


class Lead(Base):
    """Stores lead capture submissions and user sessions."""
    
    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    company_website = Column(String, nullable=False)
    work_email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=False)
    
    # Metadata
    tool_used = Column(String, nullable=False)  # e.g., "proposal-intelligence"
    session_token = Column(String(64), unique=True, index=True, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
