"""
Curato Proposal Intelligence — Recommendation Service

Generates the final recommendation with clear reasoning.
Single responsibility: synthesizing analysis into actionable recommendations.
"""

import json
from typing import Optional

from app.config import Settings
from app.schemas.proposal import ExtractedProposal
from app.schemas.comparison import ComparisonResult
from app.schemas.risk import RiskAnalysisResult
from app.schemas.recommendation import Recommendation
from app.prompts.recommendation_prompt import (
    RECOMMENDATION_SYSTEM_PROMPT,
    RECOMMENDATION_USER_PROMPT,
)
from app.services.ai_client import AIClient


class RecommendationService:
    """Generates final recommendations from analysis results."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.ai_client = AIClient(settings)

    async def generate_recommendation(
        self,
        proposals: dict[str, ExtractedProposal],
        comparison: ComparisonResult,
        risk_analysis: RiskAnalysisResult,
        session_id: str,
        max_retries: int = 3,
    ) -> Recommendation:
        """
        Generate a recommendation based on all analysis results.

        Args:
            proposals: dict of proposal_id → ExtractedProposal
            comparison: ComparisonResult from comparison engine
            risk_analysis: RiskAnalysisResult from risk engine
            session_id: The analysis session ID
            max_retries: Maximum retry attempts

        Returns:
            Recommendation with reasoning, trade-offs, and questions
        """
        proposals_data = {}
        for pid, proposal in proposals.items():
            proposals_data[proposal.agency_name] = proposal.model_dump(mode="json")

        proposals_json = json.dumps(proposals_data, indent=2, default=str)
        comparison_json = json.dumps(comparison.model_dump(mode="json"), indent=2, default=str)
        risk_json = json.dumps(risk_analysis.model_dump(mode="json"), indent=2, default=str)

        user_prompt = RECOMMENDATION_USER_PROMPT.format(
            proposals_json=proposals_json,
            comparison_json=comparison_json,
            risk_json=risk_json,
            session_id=session_id,
        )

        result = self.ai_client.generate_structured_response(
            system_prompt=RECOMMENDATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=Recommendation,
            max_retries=max_retries
        )
        return result
