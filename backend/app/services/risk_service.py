"""
Curato Proposal Intelligence — Risk Service

Analyzes proposals for risks, red flags, and concerns.
Single responsibility: risk detection and scoring.
"""

import json
from typing import Optional

from app.config import Settings
from app.schemas.proposal import ExtractedProposal
from app.schemas.risk import ProposalRiskAnalysis, RiskAnalysisResult
from app.prompts.risk_prompt import RISK_SYSTEM_PROMPT, RISK_USER_PROMPT
from app.services.ai_client import AIClient


class RiskService:
    """Detects risks and red flags in proposals."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.ai_client = AIClient(settings)

    async def analyze_risks(
        self,
        proposals: dict[str, ExtractedProposal],
        session_id: str,
        max_retries: int = 3,
    ) -> RiskAnalysisResult:
        """
        Analyze all proposals for risks.

        Args:
            proposals: dict mapping proposal_id to ExtractedProposal
            session_id: The analysis session ID
            max_retries: Maximum retry attempts

        Returns:
            RiskAnalysisResult with per-proposal risk analysis
        """
        analyses = []

        for proposal_id, proposal in proposals.items():
            analysis = await self._analyze_single_proposal(
                proposal_id=proposal_id,
                proposal=proposal,
                max_retries=max_retries,
            )
            if analysis:
                analyses.append(analysis)

        # Generate comparative insights
        comparative_insights = self._generate_comparative_insights(analyses)

        return RiskAnalysisResult(
            session_id=session_id,
            analyses=analyses,
            comparative_insights=comparative_insights,
        )

    async def _analyze_single_proposal(
        self,
        proposal_id: str,
        proposal: ExtractedProposal,
        max_retries: int = 3,
    ) -> Optional[ProposalRiskAnalysis]:
        """Analyze a single proposal for risks."""
        proposal_json = json.dumps(proposal.model_dump(mode="json"), indent=2, default=str)

        user_prompt = RISK_USER_PROMPT.format(
            agency_name=proposal.agency_name,
            proposal_id=proposal_id,
            proposal_json=proposal_json,
        )

        try:
            result = self.ai_client.generate_structured_response(
                system_prompt=RISK_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_model=ProposalRiskAnalysis,
                max_retries=max_retries
            )
            return result
        except Exception as e:
            print(f"⚠ Risk analysis failed for proposal {proposal_id}: {e}")
            return None

    def _generate_comparative_insights(
        self, analyses: list[ProposalRiskAnalysis]
    ) -> list[str]:
        """Generate comparative risk insights across proposals."""
        if len(analyses) < 2:
            return []

        insights = []

        # Compare risk scores
        sorted_by_risk = sorted(analyses, key=lambda a: a.risk_score)
        safest = sorted_by_risk[0]
        riskiest = sorted_by_risk[-1]

        if safest.agency_name != riskiest.agency_name:
            insights.append(
                f"{safest.agency_name} has the lowest risk score ({safest.risk_score}/100), "
                f"while {riskiest.agency_name} has the highest ({riskiest.risk_score}/100)."
            )

        # Compare critical risks
        for analysis in analyses:
            critical_count = sum(
                1 for r in analysis.risks if r.severity == "critical"
            )
            if critical_count > 0:
                insights.append(
                    f"{analysis.agency_name} has {critical_count} critical risk(s) "
                    f"that should be addressed before signing."
                )

        # Common risks across proposals
        all_categories = {}
        for analysis in analyses:
            for risk in analysis.risks:
                cat = risk.category
                if cat not in all_categories:
                    all_categories[cat] = []
                all_categories[cat].append(analysis.agency_name)

        for cat, agencies in all_categories.items():
            if len(agencies) == len(analyses):
                insights.append(
                    f"All proposals share a common risk in '{cat.replace('_', ' ')}' — "
                    f"this may be an industry norm worth investigating."
                )

        return insights
