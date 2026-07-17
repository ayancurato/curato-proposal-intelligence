"""
Curato Proposal Intelligence — Upload Service

Handles file validation, storage, and database record creation.
Single responsibility: managing proposal file uploads.
"""

from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import Settings
from app.models import AnalysisSession, Proposal, SessionStatus, ProposalStatus
from app.utils.file_utils import (
    generate_safe_filename,
    validate_file_extension,
    validate_file_size,
)


class UploadService:
    """Manages proposal file uploads and session creation."""

    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings

    async def handle_upload(self, files: list[UploadFile]) -> AnalysisSession:
        """
        Process multiple file uploads:
        1. Create an analysis session
        2. Validate each file
        3. Store files on disk
        4. Create database records

        Returns the created AnalysisSession with proposals.
        """
        # ── Create Session ────────────────────────────────────────
        session = AnalysisSession(status=SessionStatus.CREATED)
        self.db.add(session)
        await self.db.flush()  # Get the session ID

        errors = []

        for file in files:
            try:
                proposal = await self._process_single_file(file, session.id)
                self.db.add(proposal)
            except ValueError as e:
                errors.append(f"{file.filename}: {str(e)}")

        if errors and not session.proposals:
            # All files failed
            session.status = SessionStatus.FAILED
            session.status_message = "; ".join(errors)
        elif errors:
            # Some files failed
            session.status_message = f"Uploaded with warnings: {'; '.join(errors)}"

        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def _process_single_file(
        self, file: UploadFile, session_id: str
    ) -> Proposal:
        """Validate, store, and create a database record for a single file."""

        # ── Validate Extension ────────────────────────────────────
        if not file.filename or not validate_file_extension(file.filename):
            raise ValueError("Only PDF files are accepted.")

        # ── Read Content ──────────────────────────────────────────
        content = await file.read()
        file_size = len(content)

        # ── Validate Size ─────────────────────────────────────────
        if not validate_file_size(file_size, self.settings.max_file_size_bytes):
            max_mb = self.settings.max_file_size_mb
            raise ValueError(f"File exceeds maximum size of {max_mb} MB.")

        # ── Validate PDF Header ───────────────────────────────────
        if not content[:5] == b"%PDF-":
            raise ValueError("File does not appear to be a valid PDF.")

        # ── Store File ────────────────────────────────────────────
        safe_name = generate_safe_filename(file.filename)
        upload_dir = self.settings.upload_path
        file_path = upload_dir / safe_name

        with open(file_path, "wb") as f:
            f.write(content)

        # ── Create Record ─────────────────────────────────────────
        proposal = Proposal(
            filename=safe_name,
            original_name=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            status=ProposalStatus.UPLOADED,
            session_id=session_id,
        )

        return proposal

    async def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        """Retrieve a session by ID with its proposals."""
        result = await self.db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        return result.scalar_one_or_none()
