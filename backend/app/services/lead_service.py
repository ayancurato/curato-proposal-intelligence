"""
Curato Proposal Intelligence — Lead Service

Orchestrates lead capture, session generation, and third-party integrations.
"""

import secrets
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks

from app.config import Settings
from app.models.lead import Lead
from app.schemas.lead import LeadCreate
from app.services.turnstile_service import TurnstileService
from app.services.sheets_service import GoogleSheetsService


class LeadService:
    """Service for handling lead capture workflow."""

    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings
        self.turnstile = TurnstileService(settings)
        self.sheets = GoogleSheetsService(settings)

    async def process_lead(
        self, 
        lead_data: LeadCreate, 
        background_tasks: BackgroundTasks,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Processes a lead submission.
        
        1. Verifies Turnstile
        2. Upserts to the DB (generates session_token)
        3. Appends to Google Sheets in the background
        
        Returns:
            session_token (str)
        """
        # 1. Verify Turnstile
        is_valid = await self.turnstile.verify_token(lead_data.captcha_token, remote_ip=ip_address)
        if not is_valid:
            raise ValueError("CAPTCHA verification failed. Please try again.")

        # 2. Check if lead already exists
        result = await self.db.execute(
            select(Lead).where(Lead.work_email == lead_data.work_email)
        )
        lead = result.scalars().first()

        session_token = secrets.token_urlsafe(32)

        if lead:
            # Update existing lead
            lead.full_name = lead_data.full_name
            lead.company_name = lead_data.company_name
            lead.company_website = str(lead_data.company_website)
            lead.phone_number = lead_data.phone_number
            lead.tool_used = lead_data.tool
            lead.session_token = session_token
            lead.ip_address = ip_address
            lead.user_agent = user_agent
            # last_seen is automatically updated by SQLAlchemy onupdate
        else:
            # Create new lead
            lead = Lead(
                id=str(uuid.uuid4()),
                full_name=lead_data.full_name,
                company_name=lead_data.company_name,
                company_website=str(lead_data.company_website),
                work_email=lead_data.work_email,
                phone_number=lead_data.phone_number,
                tool_used=lead_data.tool,
                session_token=session_token,
                ip_address=ip_address,
                user_agent=user_agent
            )
            self.db.add(lead)

        await self.db.commit()

        # 3. Append to Google Sheets in the background
        background_tasks.add_task(self.sheets.append_lead, lead_data)

        return session_token

    async def validate_session(self, session_token: str) -> bool:
        """Check if a session token is valid and exists in the DB."""
        if not session_token:
            return False
            
        result = await self.db.execute(
            select(Lead).where(Lead.session_token == session_token)
        )
        lead = result.scalars().first()
        return lead is not None
