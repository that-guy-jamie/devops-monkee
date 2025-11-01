# Parallel Campaign Strategy

## Overview

The **Parallel Campaign Strategy** is an advanced campaign optimization approach that creates new, optimized campaigns alongside existing underperforming ones, allowing for a learning phase before transitioning budgets. This strategy minimizes risk and maximizes learning compared to directly modifying existing campaigns.

## Problem Statement

Traditional campaign optimization approaches face several challenges:

1. **Immediate Disruption**: Modifying an existing campaign resets its learning phase
2. **No Fallback**: If the optimization fails, you can't easily revert to the previous state
3. **Binary Decision**: You must commit fully to the change without testing
4. **Lost Historical Data**: Campaign history is disrupted by major structural changes

## Solution: Parallel Campaign Approach

Instead of modifying Campaign A directly, we:

1. **Create Campaign B**: A new campaign with optimized settings (keywords, bids, targeting, ad copy)
2. **Run in Parallel**: Both campaigns run simultaneously with split budgets
3. **Monitor Performance**: Track metrics for both campaigns during a learning period (typically 14-30 days)
4. **Gradual Transition**: Shift budget from underperforming to high-performing campaign
5. **Pause or Archive**: Once Campaign B proves superior, pause Campaign A

## Implementation in Ads Monkee

### Database Schema

The `CampaignModification` model supports parallel campaigns with these action types:

```python
class ModificationActionType(str, enum.Enum):
    # ... existing types ...
    
    # Parallel Campaign Strategy
    CREATE_PARALLEL_CAMPAIGN = "create_parallel_campaign"
    TRANSITION_BUDGET = "transition_budget"
    PAUSE_OLD_CAMPAIGN = "pause_old_campaign"
```

### Workflow

#### Phase 1: Creation
```
Action: CREATE_PARALLEL_CAMPAIGN
Status: pending → in_progress → completed

Creates:
- New campaign with optimized settings
- Initial budget split (e.g., 70% old / 30% new)
- Tracking relationship between old and new campaigns
```

#### Phase 2: Learning Period (14-30 days)
```
Action: TRANSITION_BUDGET (can be executed multiple times)
Status: pending → in_progress → completed

Adjusts:
- Budget allocation based on performance
- Example progression: 70/30 → 50/50 → 30/70 → 10/90
```

#### Phase 3: Completion
```
Action: PAUSE_OLD_CAMPAIGN
Status: pending → in_progress → completed

Finalizes:
- Pauses underperforming campaign
- Allocates 100% budget to new campaign
- Archives old campaign for historical reference
```

### Example Modification Record

```json
{
  "id": 123,
  "client_id": 1,
  "campaign_id": "22180269024",
  "modification_type": "parallel_campaign",
  "action_type": "create_parallel_campaign",
  "current_value": {
    "campaign_name": "Roofing Services 2025 - ECT/OCS",
    "daily_budget": 100.00,
    "keywords": ["roof repair", "roof replacement"],
    "bidding_strategy": "MAXIMIZE_CONVERSIONS"
  },
  "proposed_value": {
    "new_campaign_name": "Roofing Services 2025 - Optimized",
    "daily_budget_split": {
      "old_campaign": 70.00,
      "new_campaign": 30.00
    },
    "keywords": ["emergency roof repair", "affordable roof replacement", "licensed roofing contractor"],
    "bidding_strategy": "TARGET_CPA",
    "target_cpa": 50.00,
    "learning_period_days": 21
  },
  "rationale": "Current campaign has high CPA ($85) and low conversion rate (2.1%). New campaign uses more specific, high-intent keywords and Target CPA bidding to improve efficiency.",
  "expected_impact": {
    "metric": "cost_per_acquisition",
    "current": 85.00,
    "projected": 50.00,
    "confidence": 0.75
  },
  "status": "pending_approval",
  "parallel_campaign_id": null,  // Will be populated after creation
  "created_at": "2025-10-18T15:00:00Z"
}
```

## Decision Criteria

### When to Use Parallel Campaigns

✅ **Use parallel campaigns when:**
- Making significant structural changes (keywords, targeting, bidding strategy)
- Campaign has substantial historical data you want to preserve
- Budget allows for split testing
- Risk tolerance is low
- Learning period is acceptable (2-4 weeks)

❌ **Don't use parallel campaigns when:**
- Making minor adjustments (bid tweaks, ad copy variations)
- Budget is too constrained for splitting
- Immediate action is required
- Campaign is brand new (no history to preserve)

### Success Metrics

Monitor these metrics to determine when to transition:

| Metric | Threshold | Action |
|--------|-----------|--------|
| **CPA** | New campaign CPA < Old campaign CPA by 20%+ | Increase new campaign budget |
| **Conversion Rate** | New campaign CVR > Old campaign CVR by 25%+ | Increase new campaign budget |
| **ROAS** | New campaign ROAS > Old campaign ROAS by 30%+ | Increase new campaign budget |
| **Quality Score** | New campaign avg QS ≥ 7 | Maintain or increase budget |
| **Learning Phase** | New campaign exits learning phase | Begin aggressive budget transition |

### Budget Transition Schedule

**Conservative Approach (30 days):**
```
Day 1-7:   70% old / 30% new
Day 8-14:  60% old / 40% new
Day 15-21: 40% old / 60% new
Day 22-28: 20% old / 80% new
Day 29-30: 0% old / 100% new (pause old campaign)
```

**Aggressive Approach (14 days):**
```
Day 1-3:   70% old / 30% new
Day 4-7:   50% old / 50% new
Day 8-11:  30% old / 70% new
Day 12-14: 0% old / 100% new (pause old campaign)
```

## AI Recommendation Logic

The AI analysis engine should recommend parallel campaigns when:

```python
def should_recommend_parallel_campaign(campaign_data):
    """Determine if parallel campaign strategy is appropriate."""
    
    # Check if campaign has enough history
    if campaign_data['days_active'] < 30:
        return False
    
    # Check if performance is poor enough to warrant change
    if campaign_data['cpa'] > campaign_data['target_cpa'] * 1.5:
        performance_issue = True
    elif campaign_data['roas'] < campaign_data['target_roas'] * 0.7:
        performance_issue = True
    else:
        performance_issue = False
    
    if not performance_issue:
        return False
    
    # Check if budget allows for splitting
    if campaign_data['daily_budget'] < 20:  # Minimum $20/day
        return False
    
    # Check if structural changes are needed
    structural_changes_needed = (
        campaign_data['avg_quality_score'] < 5 or
        campaign_data['impression_share'] < 0.3 or
        len(campaign_data['converting_keywords']) < 3
    )
    
    return structural_changes_needed


def generate_parallel_campaign_proposal(campaign_data, analysis_results):
    """Generate a parallel campaign modification proposal."""
    
    return {
        "modification_type": "parallel_campaign",
        "action_type": "create_parallel_campaign",
        "current_value": extract_current_settings(campaign_data),
        "proposed_value": {
            "new_campaign_name": f"{campaign_data['name']} - Optimized",
            "daily_budget_split": {
                "old_campaign": campaign_data['daily_budget'] * 0.7,
                "new_campaign": campaign_data['daily_budget'] * 0.3,
            },
            "keywords": analysis_results['recommended_keywords'],
            "bidding_strategy": analysis_results['recommended_bidding_strategy'],
            "learning_period_days": 21,
            "transition_schedule": "conservative"  # or "aggressive"
        },
        "rationale": generate_rationale(campaign_data, analysis_results),
        "expected_impact": calculate_expected_impact(campaign_data, analysis_results)
    }
```

## User Interface

### Approval Dashboard

When a parallel campaign is proposed, the supervisor sees:

```
┌─────────────────────────────────────────────────────────────────┐
│ Parallel Campaign Recommendation                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Current Campaign: Roofing Services 2025 - ECT/OCS              │
│ Status: UNDERPERFORMING                                         │
│                                                                 │
│ Current Metrics (Last 30 days):                                │
│   • CPA: $85.00 (Target: $50.00) ⚠️                           │
│   • Conversion Rate: 2.1%                                       │
│   • Quality Score: 4.2/10 ⚠️                                   │
│   • Impression Share: 18.5% ⚠️                                 │
│                                                                 │
│ Proposed: Create Optimized Parallel Campaign                   │
│                                                                 │
│ Changes:                                                        │
│   • Bidding: MAXIMIZE_CONVERSIONS → TARGET_CPA ($50)          │
│   • Keywords: 12 current → 8 high-intent keywords              │
│   • Budget Split: 70% old / 30% new (initial)                 │
│   • Learning Period: 21 days                                    │
│                                                                 │
│ Expected Impact:                                                │
│   • CPA: $85 → $52 (39% improvement) 📈                        │
│   • Conversion Rate: 2.1% → 3.8% (81% improvement) 📈          │
│   • Confidence: 75%                                             │
│                                                                 │
│ Rationale:                                                      │
│   Current campaign suffers from low-quality, broad keywords    │
│   and inefficient bidding. Parallel approach allows testing    │
│   optimized settings while preserving existing performance.    │
│                                                                 │
│ [Approve] [Modify] [Reject] [Schedule for Later]              │
└─────────────────────────────────────────────────────────────────┘
```

## Monitoring and Alerts

### Automated Monitoring

The system should automatically:

1. **Track Performance**: Compare metrics between old and new campaigns daily
2. **Alert on Anomalies**: Notify if new campaign performs significantly worse than expected
3. **Suggest Budget Adjustments**: Recommend budget transitions based on performance
4. **Flag for Review**: Highlight campaigns ready for final transition

### Alert Examples

```
🟢 POSITIVE: New campaign "Roofing - Optimized" CPA is 35% lower than original
   → Recommendation: Increase budget allocation to 50/50

🟡 NEUTRAL: New campaign still in learning phase (Day 8 of 21)
   → Recommendation: Continue monitoring, no action needed

🔴 NEGATIVE: New campaign CPA is 20% higher than original after 14 days
   → Recommendation: Review and consider pausing parallel campaign
```

## Best Practices

1. **Set Clear Success Criteria**: Define metrics and thresholds before launching
2. **Allow Sufficient Learning Time**: Don't make decisions too quickly (minimum 14 days)
3. **Monitor Daily**: Check performance regularly during the learning period
4. **Document Changes**: Keep detailed notes on what was changed and why
5. **Preserve Old Campaigns**: Don't delete; pause and archive for reference
6. **Test One Variable**: When possible, change one major element at a time
7. **Budget Appropriately**: Ensure enough budget for meaningful data collection

## Integration with AI Consensus Framework

Parallel campaign recommendations should go through the multi-agent consensus process:

1. **Agent 1 (Optimizer)**: Proposes parallel campaign with aggressive optimizations
2. **Agent 2 (Conservative)**: Suggests more cautious approach or questions necessity
3. **Agent 3 (Mediator)**: Synthesizes recommendations and proposes balanced approach
4. **Final Recommendation**: Presented to human supervisor with consensus score

## Future Enhancements

- **Automated Budget Transitions**: System automatically adjusts budgets based on performance
- **A/B Testing Framework**: Extend to test multiple variations simultaneously
- **Machine Learning**: Predict optimal transition timing using historical data
- **Cross-Campaign Learning**: Apply successful strategies from one client to others
- **Risk Scoring**: Calculate risk level for each parallel campaign proposal

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-18  
**Status**: Active
