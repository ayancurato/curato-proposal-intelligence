"""
Curato Proposal Intelligence — AI Extraction Service

Converts raw proposal text into structured JSON using AIClient.
Single responsibility: AI-powered proposal data extraction.
"""

from typing import Optional

from app.config import Settings
from app.schemas.proposal import ExtractedProposal
from app.prompts.extraction_prompt import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT
from app.utils.text_utils import truncate_text
from app.services.ai_client import AIClient


class ExtractionService:
    """Extracts structured proposal data from raw text using AIClient."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.ai_client = AIClient(settings)

    async def extract_proposal(
        self, proposal_text: str, max_retries: int = 3
    ) -> ExtractedProposal:
        """
        Send proposal text to AI and extract structured data.

        Uses the AI provider's structured output capability for reliable JSON.

        Args:
            proposal_text: Cleaned text from the PDF
            max_retries: Maximum retry attempts

        Returns:
            ExtractedProposal with all extracted fields
        """
        # Truncate to avoid exceeding context limits
        text = truncate_text(proposal_text, max_chars=80_000)

        user_prompt = EXTRACTION_USER_PROMPT.format(proposal_text=text)

        extracted = self.ai_client.generate_structured_response(
            system_prompt=EXTRACTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ExtractedProposal,
            max_retries=max_retries
        )
        return extracted

