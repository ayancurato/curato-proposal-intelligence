"""
Curato Proposal Intelligence — Pipeline Service

Orchestrates the full analysis pipeline:
PDF Upload → Text Extraction → AI Extraction → Comparison → Risk → Recommendation

Single responsibility: pipeline orchestration and status management.
"""

import json
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.models import AnalysisSession, Proposal, SessionStatus, ProposalStatus
from app.schemas.proposal import ExtractedProposal
from app.schemas.comparison import ComparisonResult
from app.schemas.risk import RiskAnalysisResult
from app.schemas.recommendation import Recommendation
from app.schemas.dashboard import DashboardResponse, QuickStats
from app.schemas.session import SessionStatusEnum
from app.services.pdf_service import PDFService
from app.services.extraction_service import ExtractionService
from app.services.comparison_service import ComparisonService
from app.services.risk_service import RiskService
from app.services.recommendation_service import RecommendationService


class PipelineService:
    """Orchestrates the full proposal analysis pipeline."""

    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings

    @staticmethod
    async def run_pipeline(session_id: str, settings: Settings):
        """
        Run the complete analysis pipeline for a session.

        This method is designed to be called as a background task.
        It creates its own database session to avoid connection issues.

        Pipeline steps:
        1. Extract text from PDFs
        2. AI extraction of structured data
        3. Compare proposals
        4. Analyze risks
        5. Generate recommendation
        """
        # Create a fresh database session for the background task
        engine = create_async_engine(
            settings.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        async with session_factory() as db:
            try:
                await PipelineService._execute_pipeline(db, session_id, settings)
            except Exception as e:
                print(f"✖ Pipeline failed for session {session_id}: {e}")
                await PipelineService._update_session_status(
                    db, session_id, SessionStatus.FAILED, str(e)
                )
            finally:
                await engine.dispose()

    @staticmethod
    async def _execute_pipeline(
        db: AsyncSession, session_id: str, settings: Settings
    ):
        """Execute the pipeline steps sequentially."""

        # ── Step 1: Text Extraction ───────────────────────────────
        print(f"▸ Step 1/5: Extracting text from PDFs...")
        await PipelineService._update_session_status(
            db, session_id, SessionStatus.EXTRACTING, "Extracting text from PDFs..."
        )

        result = await db.execute(
            select(Proposal).where(Proposal.session_id == session_id)
        )
        proposals = list(result.scalars().all())

        if not proposals:
            raise ValueError("No proposals found in session.")

        for proposal in proposals:
            try:
                proposal.status = ProposalStatus.EXTRACTING_TEXT
                await db.commit()

                text, page_count = await PDFService.extract_text(proposal.file_path)
                proposal.raw_text = text
                proposal.page_count = page_count
                proposal.status = ProposalStatus.EXTRACTED_TEXT
                await db.commit()

                print(f"  ✓ Extracted {len(text)} chars from {proposal.original_name}")

            except Exception as e:
                proposal.status = ProposalStatus.FAILED
                proposal.error_message = str(e)
                await db.commit()
                print(f"  ✖ Failed: {proposal.original_name}: {e}")

        # Check if we have at least 2 proposals for comparison
        valid_proposals = [p for p in proposals if p.status == ProposalStatus.EXTRACTED_TEXT]
        if len(valid_proposals) < 1:
            raise ValueError("No proposals could be text-extracted.")

        # ── Step 2: AI Extraction ─────────────────────────────────
        print(f"▸ Step 2/5: AI extracting structured data...")
        await PipelineService._update_session_status(
            db, session_id, SessionStatus.EXTRACTING,
            "AI is analyzing proposal content..."
        )

        extraction_service = ExtractionService(settings)
        extracted_proposals: dict[str, ExtractedProposal] = {}

        for proposal in valid_proposals:
            try:
                proposal.status = ProposalStatus.ANALYZING
                await db.commit()

                extracted = await extraction_service.extract_proposal(proposal.raw_text)
                proposal.extracted_data = json.dumps(
                    extracted.model_dump(mode="json"), default=str
                )
                proposal.status = ProposalStatus.EXTRACTED
                await db.commit()

                extracted_proposals[proposal.id] = extracted
                print(f"  ✓ Extracted: {extracted.agency_name}")

            except Exception as e:
                proposal.status = ProposalStatus.FAILED
                proposal.error_message = str(e)
                await db.commit()
                print(f"  ✖ AI extraction failed: {proposal.original_name}: {e}")

        if len(extracted_proposals) < 1:
            raise ValueError("No proposals could be AI-extracted.")

        # ── Step 3: Comparison or Review ──────────────────────────
        comparison_result = None
        if len(extracted_proposals) == 1:
            print(f"▸ Step 3/5: Analyzing single proposal...")
            await PipelineService._update_session_status(
                db, session_id, SessionStatus.COMPARING,
                "Analyzing proposal across dimensions..."
            )
            from app.services.review_service import ReviewService
            review_service = ReviewService(settings)
            comparison_result = await review_service.review_proposal(
                extracted_proposals, session_id
            )

            # Store comparison data in session
            session_obj = await db.get(AnalysisSession, session_id)
            session_obj.comparison_data = json.dumps(
                comparison_result.model_dump(mode="json"), default=str
            )
            await db.commit()
            print(f"  ✓ Analysis complete")

        elif len(extracted_proposals) >= 2:
            print(f"▸ Step 3/5: Comparing proposals...")
            await PipelineService._update_session_status(
                db, session_id, SessionStatus.COMPARING,
                "Comparing proposals across dimensions..."
            )

            comparison_service = ComparisonService(settings)
            comparison_result = await comparison_service.compare_proposals(
                extracted_proposals, session_id
            )

            # Store comparison data in session
            session_obj = await db.get(AnalysisSession, session_id)
            session_obj.comparison_data = json.dumps(
                comparison_result.model_dump(mode="json"), default=str
            )
            await db.commit()
            print(f"  ✓ Comparison complete")
        else:
            print(f"▸ Step 3/5: Skipped")

        # ── Step 4: Risk Analysis ─────────────────────────────────
        print(f"▸ Step 4/5: Analyzing risks...")
        await PipelineService._update_session_status(
            db, session_id, SessionStatus.ANALYZING_RISKS,
            "Identifying risks and red flags..."
        )

        risk_service = RiskService(settings)
        risk_result = await risk_service.analyze_risks(
            extracted_proposals, session_id
        )

        # Store risk data per proposal
        for analysis in risk_result.analyses:
            for proposal in proposals:
                if proposal.id == analysis.proposal_id:
                    proposal.risks = json.dumps(
                        analysis.model_dump(mode="json"), default=str
                    )
                    await db.commit()
                    break

        print(f"  ✓ Risk analysis complete")

        # ── Step 5: Recommendation or Verdict ─────────────────────
        recommendation_result = None
        if len(extracted_proposals) == 1 and comparison_result:
            print(f"▸ Step 5/5: Generating final verdict...")
            await PipelineService._update_session_status(
                db, session_id, SessionStatus.RECOMMENDING,
                "Generating final AI verdict..."
            )
            from app.services.review_service import ReviewService
            review_service = ReviewService(settings)
            recommendation_result = await review_service.generate_verdict(
                extracted_proposals, comparison_result, risk_result, session_id
            )
            session_obj = await db.get(AnalysisSession, session_id)
            session_obj.recommendation_data = json.dumps(
                recommendation_result.model_dump(mode="json"), default=str
            )
            await db.commit()
            print(f"  ✓ Verdict complete")

        elif len(extracted_proposals) >= 2 and comparison_result:
            print(f"▸ Step 5/5: Generating recommendation...")
            await PipelineService._update_session_status(
                db, session_id, SessionStatus.RECOMMENDING,
                "Generating intelligent recommendation..."
            )

            recommendation_service = RecommendationService(settings)
            recommendation_result = await recommendation_service.generate_recommendation(
                extracted_proposals, comparison_result, risk_result, session_id
            )

            session_obj = await db.get(AnalysisSession, session_id)
            session_obj.recommendation_data = json.dumps(
                recommendation_result.model_dump(mode="json"), default=str
            )
            await db.commit()
            print(f"  ✓ Recommendation: {recommendation_result.best_fit_agency}")
        else:
            print(f"▸ Step 5/5: Skipped")

        # ── Mark Complete ─────────────────────────────────────────
        await PipelineService._update_session_status(
            db, session_id, SessionStatus.COMPLETED,
            "Analysis complete!"
        )
        print(f"✦ Pipeline complete for session {session_id}")

    @staticmethod
    async def _update_session_status(
        db: AsyncSession,
        session_id: str,
        status: SessionStatus,
        message: str,
    ):
        """Update the session status and message."""
        session = await db.get(AnalysisSession, session_id)
        if session:
            session.status = status
            session.status_message = message
            await db.commit()

    async def get_dashboard_response(self, session_id: str) -> Optional[DashboardResponse]:
        """
        Build the unified dashboard response from stored data.
        The frontend should never need to perform business logic.
        """
        session = await self.db.get(AnalysisSession, session_id)
        if not session:
            return None

        result = await self.db.execute(
            select(Proposal).where(Proposal.session_id == session_id)
        )
        proposals = list(result.scalars().all())

        # Parse stored JSON data
        comparison = None
        if session.comparison_data:
            try:
                comparison = ComparisonResult.model_validate(
                    json.loads(session.comparison_data)
                )
            except Exception:
                pass

        recommendation = None
        if session.recommendation_data:
            try:
                recommendation = Recommendation.model_validate(
                    json.loads(session.recommendation_data)
                )
            except Exception:
                pass

        # Build risk analysis from per-proposal data
        from app.schemas.risk import ProposalRiskAnalysis, RiskAnalysisResult
        risk_analyses = []
        for proposal in proposals:
            if proposal.risks:
                try:
                    risk_analysis = ProposalRiskAnalysis.model_validate(
                        json.loads(proposal.risks)
                    )
                    risk_analyses.append(risk_analysis)
                except Exception:
                    pass

        risk_result = RiskAnalysisResult(
            session_id=session_id,
            analyses=risk_analyses,
        ) if risk_analyses else None

        # Build proposal read objects
        from app.schemas.proposal import ProposalRead, ExtractedProposal as EP
        proposal_reads = []
        for p in proposals:
            extracted = None
            if p.extracted_data:
                try:
                    extracted = EP.model_validate(json.loads(p.extracted_data))
                except Exception:
                    pass

            proposal_reads.append(ProposalRead(
                id=p.id,
                filename=p.filename,
                original_name=p.original_name,
                file_size=p.file_size,
                page_count=p.page_count,
                status=p.status,
                error_message=p.error_message,
                extracted_data=extracted,
                session_id=p.session_id,
                created_at=p.created_at,
                updated_at=p.updated_at,
            ))

        # ── Compute Quick Stats ───────────────────────────────────
        quick_stats = self._compute_quick_stats(
            proposal_reads, risk_result, recommendation
        )

        return DashboardResponse(
            session_id=session_id,
            status=session.status,
            status_message=session.status_message,
            proposals=proposal_reads,
            proposal_count=len(proposals),
            comparison=comparison,
            risk_analysis=risk_result,
            recommendation=recommendation,
            quick_stats=quick_stats,
        )

    def _compute_quick_stats(
        self,
        proposals: list,
        risk_result: Optional[RiskAnalysisResult],
        recommendation: Optional[Recommendation],
    ) -> QuickStats:
        """Pre-compute dashboard statistics."""
        prices = []
        for p in proposals:
            if p.extracted_data and p.extracted_data.pricing.total_cost:
                prices.append(p.extracted_data.pricing.total_cost)

        total_risks = 0
        critical_risks = 0
        high_risks = 0
        if risk_result:
            for analysis in risk_result.analyses:
                total_risks += len(analysis.risks)
                critical_risks += sum(
                    1 for r in analysis.risks if r.severity == "critical"
                )
                high_risks += sum(
                    1 for r in analysis.risks if r.severity == "high"
                )

        return QuickStats(
            total_proposals=len(proposals),
            price_range_min=min(prices) if prices else None,
            price_range_max=max(prices) if prices else None,
            total_risks=total_risks,
            critical_risks=critical_risks,
            high_risks=high_risks,
            recommended_agency=(
                recommendation.best_fit_agency if recommendation else None
            ),
            confidence_level=(
                recommendation.confidence_level if recommendation else None
            ),
            health_score=(
                recommendation.assessments[0].overall_score 
                if recommendation and recommendation.assessments and len(proposals) == 1 else None
            ),
        )
