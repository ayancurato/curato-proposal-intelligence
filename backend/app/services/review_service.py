"""
Curato Proposal Intelligence — Review Service

Handles Single Proposal Analysis (when only 1 proposal is uploaded).
"""

import json

from app.config import Settings
from app.schemas.proposal import ExtractedProposal
from app.schemas.comparison import ComparisonResult
from app.schemas.risk import RiskAnalysisResult
from app.schemas.recommendation import Recommendation
from app.prompts.review_prompt import REVIEW_SYSTEM_PROMPT, REVIEW_USER_PROMPT
from app.prompts.verdict_prompt import VERDICT_SYSTEM_PROMPT, VERDICT_USER_PROMPT
from app.services.ai_client import AIClient


class ReviewService:
    """Provides deep analysis and a final verdict for a single proposal."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.ai_client = AIClient(settings)

    async def review_proposal(
        self,
        proposals: dict[str, ExtractedProposal],
        session_id: str,
        max_retries: int = 3,
    ) -> ComparisonResult:
        """
        Analyze a single proposal across business dimensions.
        Reuses the ComparisonResult schema for frontend compatibility.
        """
        # There should only be one proposal
        proposal_id, proposal = next(iter(proposals.items()))
        
        proposal_json = json.dumps(proposal.model_dump(mode="json"), indent=2, default=str)

        user_prompt = REVIEW_USER_PROMPT.format(
            session_id=session_id,
            proposal_json=proposal_json,
        )

        result = self.ai_client.generate_structured_response(
            system_prompt=REVIEW_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ComparisonResult,
            max_retries=max_retries
        )
        return result

    async def generate_verdict(
        self,
        proposals: dict[str, ExtractedProposal],
        analysis_result: ComparisonResult,
        risk_result: RiskAnalysisResult,
        session_id: str,
        max_retries: int = 3,
    ) -> Recommendation:
        """
        Generate a final AI verdict for a single proposal.
        Reuses the Recommendation schema for frontend compatibility.
        """
        proposal_id, proposal = next(iter(proposals.items()))
        
        proposal_json = json.dumps(proposal.model_dump(mode="json"), indent=2, default=str)
        analysis_json = json.dumps(analysis_result.model_dump(mode="json"), indent=2, default=str)
        risk_json = json.dumps(risk_result.model_dump(mode="json"), indent=2, default=str)

        user_prompt = VERDICT_USER_PROMPT.format(
            session_id=session_id,
            proposal_json=proposal_json,
            analysis_json=analysis_json,
            risk_json=risk_json,
        )

        result = self.ai_client.generate_structured_response(
            system_prompt=VERDICT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=Recommendation,
            max_retries=max_retries
        )
        return result
