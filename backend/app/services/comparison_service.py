"""
Curato Proposal Intelligence — Comparison Service

Compares multiple proposals across 10 business dimensions using AIClient.
Single responsibility: multi-proposal comparison.
"""

import json
from typing import Optional

from app.config import Settings
from app.schemas.proposal import ExtractedProposal
from app.schemas.comparison import ComparisonResult
from app.prompts.comparison_prompt import COMPARISON_SYSTEM_PROMPT, COMPARISON_USER_PROMPT
from app.services.ai_client import AIClient


class ComparisonService:
    """Compares multiple proposals across key business dimensions."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.ai_client = AIClient(settings)

    async def compare_proposals(
        self,
        proposals: dict[str, ExtractedProposal],
        session_id: str,
        max_retries: int = 3,
    ) -> ComparisonResult:
        """
        Compare multiple proposals across all business dimensions.

        Args:
            proposals: dict mapping proposal_id to ExtractedProposal
            session_id: The analysis session ID
            max_retries: Maximum retry attempts

        Returns:
            ComparisonResult with per-dimension scoring
        """
        # Serialize proposals for the prompt
        proposals_data = {}
        for pid, proposal in proposals.items():
            proposals_data[proposal.agency_name] = proposal.model_dump(mode="json")

        proposals_json = json.dumps(proposals_data, indent=2, default=str)

        user_prompt = COMPARISON_USER_PROMPT.format(
            proposals_json=proposals_json,
            session_id=session_id,
            proposal_count=len(proposals),
        )

        result = self.ai_client.generate_structured_response(
            system_prompt=COMPARISON_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ComparisonResult,
            max_retries=max_retries
        )
        return result

