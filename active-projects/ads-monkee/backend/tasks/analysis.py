"""
Analysis Tasks
==============

Celery tasks for AI-driven campaign analysis.

Week 1: Stub implementations that return dummy data.
Week 2: Implement actual AI logic.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict
from uuid import UUID

from celery import chain, shared_task
from sqlalchemy import text

from backend.celery_app import celery_app
from backend.database import get_sync_db
from backend.models import (
    AnalysisRecommendation,
    AnalysisReport,
    AnalysisRun,
    AnalysisRunPhase,
    AnalysisRunStatus,
)
from backend.schemas.analysis import (
    AnalysisContext,
    BiddingBudgetModuleOutput,
    KeywordQueryModuleOutput,
    ParallelCampaignProposal,
    Recommendation,
    Synthesis,
)


# ==============================================================================
# Task 1: Prepare Data
# ==============================================================================

@shared_task(bind=True, name="backend.tasks.analysis.prepare_data_task")
def prepare_data_task(self, client_id: int, run_id: str, window_days: int = 30) -> Dict:
    """
    Prepare analysis context from focus views and aggregates.
    
    This task:
    1. Queries focus views (token-capped)
    2. Queries aggregate summaries
    3. Fetches client targets
    4. Builds compact context dict
    5. Computes feature hash for caching
    
    Args:
        client_id: Client ID
        run_id: Analysis run UUID
        window_days: Analysis window in days
    
    Returns:
        AnalysisContext as dict
    """
    print(f"[PREPARE] Starting for client {client_id}, run {run_id}")
    
    # Update run status
    with get_sync_db() as db:
        run = db.query(AnalysisRun).filter(AnalysisRun.run_id == UUID(run_id)).first()
        if run:
            run.status = AnalysisRunStatus.RUNNING
            run.current_phase = AnalysisRunPhase.PREPARE
            run.progress_pct = 10
            run.started_at = datetime.utcnow()
            db.commit()
    
    # STUB IMPLEMENTATION (Week 1)
    # Week 2: Replace with actual queries to focus views
    context = AnalysisContext(
        client_id=client_id,
        window_days=window_days,
        campaigns_summary=[
            {
                "campaign_id": "12345",
                "campaign_name": "Brand Campaign",
                "total_cost": 1500.00,
                "total_conversions": 25,
                "cpa": 60.00,
            }
        ],
        focus_keywords=[
            {
                "keyword_id": "67890",
                "keyword_text": "roofing services",
                "total_cost": 300.00,
                "total_conversions": 0,
                "issue_type": "high_spend_no_conv",
            }
        ],
        focus_search_terms=[
            {
                "search_term": "free roofing estimate",
                "total_cost": 150.00,
                "total_conversions": 0,
                "issue_type": "high_spend_no_conv",
            }
        ],
        focus_segments=[],
        target_cpa=50.00,
        target_roas=4.0,
        monthly_budget=5000.00,
    )
    
    # Compute feature hash for caching
    feature_str = json.dumps(context.model_dump(), sort_keys=True)
    feature_hash = hashlib.sha256(feature_str.encode()).hexdigest()
    context.feature_hash = feature_hash
    
    print(f"[PREPARE] Context built. Feature hash: {feature_hash[:8]}...")
    
    # Update run with feature hash
    with get_sync_db() as db:
        run = db.query(AnalysisRun).filter(AnalysisRun.run_id == UUID(run_id)).first()
        if run:
            run.feature_hash = feature_hash
            run.progress_pct = 20
            db.commit()
    
    return context.model_dump()


# ==============================================================================
# Task 2: Analyze Keywords & Queries
# ==============================================================================

@shared_task(bind=True, name="backend.tasks.analysis.analyze_keywords_and_queries")
def analyze_keywords_and_queries(self, context: Dict) -> Dict:
    """
    Analyze keywords and search terms for issues.
    
    This task:
    1. Analyzes focus_keywords for poor performers
    2. Analyzes focus_search_terms for negative keyword candidates
    3. Generates recommendations
    
    Args:
        context: AnalysisContext from prepare_data_task
    
    Returns:
        KeywordQueryModuleOutput as dict
    """
    print(f"[KEYWORDS] Starting analysis for client {context['client_id']}")
    
    # STUB IMPLEMENTATION (Week 1)
    # Week 2: Replace with actual LLM call
    output = KeywordQueryModuleOutput(
        negative_keywords_to_add=["free", "cheap", "discount"],
        keywords_to_pause=[
            {"keyword_id": "67890", "reason": "High spend, zero conversions"}
        ],
        search_terms_with_issues=[
            {"search_term": "free roofing estimate", "reason": "$150 spent, 0 conversions"}
        ],
        recommendations=[
            Recommendation(
                entity_type="search_term",
                entity_id="free roofing estimate",
                category="query_hygiene",
                action="add_negative",
                rationale_md="This search term has spent $150 with zero conversions. It indicates users looking for free services, which doesn't align with business goals.",
                expected_impact={"monthly_savings": 150.00},
                risk="low",
                confidence=0.85,
            )
        ],
    )
    
    print(f"[KEYWORDS] Found {len(output.recommendations)} recommendations")
    
    return output.model_dump()


# ==============================================================================
# Task 3: Analyze Bidding & Budget
# ==============================================================================

@shared_task(bind=True, name="backend.tasks.analysis.analyze_bidding")
def analyze_bidding(self, context: Dict, keywords_output: Dict) -> Dict:
    """
    Analyze bidding strategies and budget allocation.
    
    This task:
    1. Analyzes campaign-level performance
    2. Identifies budget reallocation opportunities
    3. Suggests bidding strategy changes
    
    Args:
        context: AnalysisContext from prepare_data_task
        keywords_output: Output from analyze_keywords_and_queries
    
    Returns:
        BiddingBudgetModuleOutput as dict
    """
    print(f"[BIDDING] Starting analysis for client {context['client_id']}")
    
    # STUB IMPLEMENTATION (Week 1)
    # Week 2: Replace with actual LLM call
    output = BiddingBudgetModuleOutput(
        bidding_strategy_recommendations=[
            {
                "campaign_id": "12345",
                "current_strategy": "Manual CPC",
                "recommended_strategy": "Target CPA",
                "reason": "Campaign has sufficient conversion data for automated bidding",
            }
        ],
        budget_reallocation=[
            {
                "from_campaign": "12345",
                "to_campaign": "67890",
                "amount": 500.00,
                "reason": "Campaign 67890 has lower CPA and room to scale",
            }
        ],
        recommendations=[
            Recommendation(
                entity_type="campaign",
                entity_id="12345",
                category="bidding",
                action="change_bid",
                rationale_md="Campaign has 25+ conversions in the last 30 days. Switching to Target CPA bidding could reduce CPA by 15-20%.",
                expected_impact={"cpa_reduction_pct": -17.5},
                risk="medium",
                confidence=0.70,
            )
        ],
    )
    
    print(f"[BIDDING] Found {len(output.recommendations)} recommendations")
    
    return output.model_dump()


# ==============================================================================
# Task 4: Synthesize
# ==============================================================================

@shared_task(bind=True, name="backend.tasks.analysis.synthesize_task")
def synthesize_task(
    self,
    context: Dict,
    keywords_output: Dict,
    bidding_output: Dict
) -> Dict:
    """
    Synthesize module outputs into final recommendations.
    
    This task:
    1. Merges recommendations from all modules
    2. Ranks by impact and confidence
    3. Identifies parallel campaign opportunities
    4. Calculates health score
    5. Generates top issues list
    
    Args:
        context: AnalysisContext from prepare_data_task
        keywords_output: Output from analyze_keywords_and_queries
        bidding_output: Output from analyze_bidding
    
    Returns:
        Synthesis as dict
    """
    print(f"[SYNTHESIS] Starting for client {context['client_id']}")
    
    # Parse module outputs
    kw_module = KeywordQueryModuleOutput(**keywords_output)
    bid_module = BiddingBudgetModuleOutput(**bidding_output)
    
    # Merge recommendations
    all_recommendations = kw_module.recommendations + bid_module.recommendations
    
    # STUB IMPLEMENTATION (Week 1)
    # Week 2: Replace with actual LLM-driven synthesis
    synthesis = Synthesis(
        health_score=6.5,
        top_issues=[
            "High spend on non-converting search terms ($300/month wasted)",
            "Manual bidding limiting scale potential",
            "CPA 20% above target ($60 vs $50 target)",
        ],
        recommendations=all_recommendations,
        parallel_campaign=ParallelCampaignProposal(
            original_campaign_id="12345",
            original_campaign_name="Brand Campaign",
            proposed_campaign_name="Brand Campaign - Optimized",
            original_budget_pct=0.7,
            new_budget_pct=0.3,
            keyword_changes={
                "remove": ["roofing services"],  # Poor performer
                "add": ["professional roofing contractor"],  # Better intent
            },
            bidding_strategy_change="Target CPA",
            target_cpa=50.00,
            learning_period_days=21,
            transition_schedule="conservative",
            expected_cpa_improvement=20.0,
            expected_conversion_rate_improvement=15.0,
            confidence=0.75,
        ),
        analysis_window_days=context["window_days"],
        data_quality_score=0.95,
        confidence_notes=[
            "Sufficient data for recommendations (30 days, 25 conversions)",
            "Parallel campaign proposal based on proven optimization patterns",
        ],
    )
    
    print(f"[SYNTHESIS] Generated {len(synthesis.recommendations)} recommendations")
    print(f"[SYNTHESIS] Health score: {synthesis.health_score}/10")
    
    return synthesis.model_dump()


# ==============================================================================
# Task 5: Persist
# ==============================================================================

@shared_task(bind=True, name="backend.tasks.analysis.persist_task")
def persist_task(
    self,
    client_id: int,
    run_id: str,
    synthesis: Dict
) -> Dict:
    """
    Persist analysis results to database.
    
    This task:
    1. Stores Synthesis as JSON in analysis_reports
    2. Generates Markdown report
    3. Normalizes recommendations to analysis_recommendations
    4. Updates run status to DONE
    5. Records cost metrics
    
    Args:
        client_id: Client ID
        run_id: Analysis run UUID
        synthesis: Synthesis output from synthesize_task
    
    Returns:
        Success status
    """
    print(f"[PERSIST] Starting for client {client_id}, run {run_id}")
    
    # Parse synthesis
    synth = Synthesis(**synthesis)
    
    # Generate Markdown (stub)
    markdown = f"""# Analysis Report
    
## Health Score: {synth.health_score}/10

## Top Issues

{chr(10).join(f"- {issue}" for issue in synth.top_issues)}

## Recommendations

{len(synth.recommendations)} recommendations generated.

## Parallel Campaign Proposal

{"Yes - see details in JSON" if synth.parallel_campaign else "No parallel campaign recommended"}
"""
    
    # Persist to database
    with get_sync_db() as db:
        # Get run
        run = db.query(AnalysisRun).filter(AnalysisRun.run_id == UUID(run_id)).first()
        if not run:
            raise ValueError(f"Run {run_id} not found")
        
        # Create report
        report = AnalysisReport(
            run_id=UUID(run_id),
            json=synth.model_dump(),
            markdown=markdown,
            health_score=synth.health_score,
            top_issues_count=len(synth.top_issues),
            recommendations_count=len(synth.recommendations),
            has_parallel_campaign=(synth.parallel_campaign is not None),
        )
        db.add(report)
        
        # Create recommendation records
        for rec in synth.recommendations:
            db_rec = AnalysisRecommendation(
                run_id=UUID(run_id),
                entity_type=rec.entity_type,
                entity_id=rec.entity_id,
                category=rec.category,
                action=rec.action,
                rationale_md=rec.rationale_md,
                expected_impact=rec.expected_impact,
                risk=rec.risk,
                confidence=rec.confidence,
                prerequisites=rec.prerequisites,
            )
            db.add(db_rec)
        
        # Update run status
        run.status = AnalysisRunStatus.DONE
        run.current_phase = AnalysisRunPhase.PERSIST
        run.progress_pct = 100
        run.finished_at = datetime.utcnow()
        run.model = "stub-v1"  # Week 2: Replace with actual model name
        run.prompt_version = "v1.0.0"
        
        # STUB: Cost tracking (Week 2: Replace with actual costs)
        run.input_tokens = 1500
        run.output_tokens = 800
        run.cost_usd = 0.05
        
        db.commit()
    
    print(f"[PERSIST] Analysis complete! Run {run_id} saved.")
    
    # TODO: Send notification (Week 4)
    # notify_supervisor(client_id, run_id)
    
    return {"ok": True, "run_id": run_id}


# ==============================================================================
# Main Analysis Chain
# ==============================================================================

def run_full_analysis(client_id: int, run_id: str, window_days: int = 30):
    """
    Execute full analysis pipeline as a Celery chain.
    
    This chains all tasks together in sequence:
    prepare → keywords → bidding → synthesis → persist
    
    Args:
        client_id: Client ID
        run_id: Analysis run UUID
        window_days: Analysis window in days
    
    Returns:
        Celery chain result
    """
    print(f"[ANALYSIS] Starting full analysis for client {client_id}")
    
    # Create the task chain
    # Each task passes its output to the next task
    return chain(
        prepare_data_task.s(client_id, run_id, window_days),
        analyze_keywords_and_queries.s(),
        analyze_bidding.s(),
        synthesize_task.s(),
        persist_task.s(client_id, run_id),
    )()

