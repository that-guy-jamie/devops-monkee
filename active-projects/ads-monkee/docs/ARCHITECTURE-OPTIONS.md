# Ads Monkee - Architecture Options

## Option A: Standalone Analysis Service

```
┌─────────────────┐
│  Google Ads API │
└────────┬────────┘
         │ Pull data
         ▼
┌─────────────────┐
│   PostgreSQL    │◄─── CSV Import (historical)
│   (Render)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│     AI Analysis Service (Render)        │
│  ┌─────────────────────────────────┐   │
│  │  Analysis Engine                │   │
│  │  • Data aggregation             │   │
│  │  • Prompt engineering           │   │
│  │  • Multi-agent consensus        │   │
│  │  • Report generation            │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  AI Providers                   │   │
│  │  • OpenAI (GPT-4)              │   │
│  │  • Anthropic (Claude)          │   │
│  │  • Local models (optional)     │   │
│  └─────────────────────────────────┘   │
└────────┬────────────────────────────────┘
         │
         ├──────────────────┬─────────────────┐
         ▼                  ▼                 ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
│  Supervisor     │  │  PostgreSQL  │  │  GHL API     │
│  Dashboard      │  │  (Store      │  │  (Notify     │
│  (React/Next)   │  │  Results)    │  │  Client)     │
└─────────────────┘  └──────────────┘  └──────────────┘
```

### Pros
✅ Full control over AI logic  
✅ Can use any AI model/provider  
✅ Independent scaling  
✅ Custom prompt engineering  
✅ Not dependent on GHL  

### Cons
❌ More to build from scratch  
❌ Manage AI API costs directly  
❌ Handle scheduling/orchestration  
❌ More infrastructure to maintain  

---

## Option B: GHL-Native Analysis

```
┌─────────────────┐
│  Google Ads API │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (Render)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         GoHighLevel (GHL)               │
│  ┌─────────────────────────────────┐   │
│  │  Workflow Automation            │   │
│  │  • Trigger: New data available  │   │
│  │  • Action: Run AI analysis      │   │
│  │  • Action: Send to supervisor   │   │
│  │  • Action: Notify client        │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  GHL AI Features                │   │
│  │  • Built-in AI capabilities     │   │
│  │  • Prompt templates             │   │
│  │  • Report generation            │   │
│  └─────────────────────────────────┘   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Supervisor     │
│  Dashboard      │
│  (in GHL)       │
└─────────────────┘
```

### Pros
✅ Leverage existing GHL infrastructure  
✅ Use GHL's workflow automation  
✅ Simpler deployment  
✅ All in one platform  
✅ GHL handles client communication  

### Cons
❌ Limited control over AI prompts  
❌ Dependent on GHL's AI capabilities  
❌ May be constrained by GHL's data handling  
❌ Less flexibility for custom logic  
❌ Harder to implement multi-agent consensus  

---

## Option C: Hybrid Approach (RECOMMENDED)

```
┌─────────────────┐
│  Google Ads API │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │◄─── Historical data
│   (Render)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│     AI Analysis Service (Render)        │
│  ┌─────────────────────────────────┐   │
│  │  Core Analysis Engine           │   │
│  │  • Data prep & aggregation      │   │
│  │  • Multi-agent consensus        │   │
│  │  • Recommendation generation    │   │
│  │  • Confidence scoring           │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  AI Orchestration               │   │
│  │  Agent 1: Optimizer (GPT-4)    │   │
│  │  Agent 2: Conservative (Claude) │   │
│  │  Agent 3: Mediator (GPT-4)     │   │
│  └─────────────────────────────────┘   │
└────────┬────────────────────────────────┘
         │
         ├──────────────────┬─────────────────┐
         ▼                  ▼                 ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────────┐
│  Supervisor     │  │  PostgreSQL  │  │  GHL Integration │
│  Dashboard      │  │  (Results)   │  │  ┌────────────┐  │
│  (React/Next)   │  └──────────────┘  │  │ Webhooks   │  │
│  • Review       │                     │  │ Workflows  │  │
│  • Approve      │                     │  │ Notify     │  │
│  • Modify       │                     │  └────────────┘  │
└─────────────────┘                     └──────────────────┘
         │                                        │
         └────────────────┬───────────────────────┘
                          ▼
                 ┌─────────────────┐
                 │  Campaign       │
                 │  Modifications  │
                 │  (Apply to      │
                 │  Google Ads)    │
                 └─────────────────┘
```

### Pros
✅ Best of both worlds  
✅ Full control over analysis logic  
✅ GHL handles client communication  
✅ Can evolve independently  
✅ Flexible AI model selection  
✅ Custom multi-agent implementation  

### Cons
❌ Most complex architecture  
❌ Need to maintain integration layer  
❌ Potential for sync issues  
❌ More moving parts  

---

## Recommended Implementation: Hybrid (Option C)

### Phase 1: Core Analysis Service (Week 1-2)
```python
# Simplified flow
1. Celery task triggers analysis (scheduled or on-demand)
2. Fetch client data from PostgreSQL
3. Prepare analysis context (aggregate, filter, format)
4. Run multi-agent analysis:
   - Agent 1 (Optimizer): Aggressive recommendations
   - Agent 2 (Conservative): Risk-averse approach
   - Agent 3 (Mediator): Synthesize consensus
5. Generate structured results + human-readable report
6. Store in PostgreSQL (reports table)
7. Notify supervisor (email/dashboard alert)
```

### Phase 2: GHL Integration (Week 3)
```python
# Add GHL hooks
1. Analysis complete → Webhook to GHL
2. GHL workflow:
   - Create task for supervisor
   - Send notification to client
   - Log in client timeline
3. Supervisor approves in dashboard
4. Dashboard → GHL API: Update status
5. GHL → Client: "Changes approved, implementing..."
```

### Phase 3: Automation (Week 4+)
```python
# Advanced features
1. Auto-approve low-risk changes
2. Schedule parallel campaign creation
3. Monitor performance automatically
4. Alert on anomalies
5. Learn from historical approvals
```

---

## Analysis Pipeline Detail

### Data Preparation
```python
def prepare_analysis_context(client_id: str, date_range: tuple):
    """Prepare data for AI analysis."""
    
    # 1. Aggregate campaign metrics
    campaigns = aggregate_campaign_performance(client_id, date_range)
    
    # 2. Identify underperformers
    issues = identify_performance_issues(campaigns)
    
    # 3. Get keyword details for problem campaigns
    keywords = get_keyword_details(issues.campaign_ids)
    
    # 4. Get search terms for context
    search_terms = get_top_search_terms(issues.campaign_ids, limit=100)
    
    # 5. Calculate benchmarks
    benchmarks = calculate_industry_benchmarks(client_id)
    
    return {
        "campaigns": campaigns,
        "issues": issues,
        "keywords": keywords,
        "search_terms": search_terms,
        "benchmarks": benchmarks,
        "client_goals": get_client_goals(client_id)
    }
```

### Multi-Agent Analysis
```python
async def run_multi_agent_analysis(context: dict):
    """Run 3-agent consensus analysis."""
    
    # Agent 1: Optimizer (aggressive)
    optimizer_prompt = build_optimizer_prompt(context)
    optimizer_response = await openai.chat(model="gpt-4", prompt=optimizer_prompt)
    
    # Agent 2: Conservative (risk-averse)
    conservative_prompt = build_conservative_prompt(context)
    conservative_response = await anthropic.chat(model="claude-3-sonnet", prompt=conservative_prompt)
    
    # Agent 3: Mediator (synthesize)
    mediator_prompt = build_mediator_prompt(context, optimizer_response, conservative_response)
    mediator_response = await openai.chat(model="gpt-4", prompt=mediator_prompt)
    
    # Generate consensus
    consensus = synthesize_consensus(optimizer_response, conservative_response, mediator_response)
    
    return {
        "consensus": consensus,
        "agent_responses": {
            "optimizer": optimizer_response,
            "conservative": conservative_response,
            "mediator": mediator_response
        }
    }
```

### Cost Optimization
```python
def optimize_analysis_cost(client_data: dict):
    """Reduce AI costs while maintaining quality."""
    
    # 1. Pre-filter data
    # Only send underperforming campaigns to AI
    filtered = filter_to_problem_areas(client_data)
    
    # 2. Aggregate metrics
    # Send summaries instead of raw data
    aggregated = aggregate_to_summaries(filtered)
    
    # 3. Use tiered approach
    # Quick check with cheaper model first
    quick_check = await openai.chat(model="gpt-3.5-turbo", prompt=triage_prompt)
    
    if quick_check.severity == "high":
        # Deep dive with expensive model
        deep_analysis = await openai.chat(model="gpt-4", prompt=detailed_prompt)
    else:
        # Use quick check results
        deep_analysis = quick_check
    
    return deep_analysis
```

---

## Cost Estimates

### Per-Client Monthly Costs (Hybrid Approach)

| Component | Frequency | Cost/Run | Monthly |
|-----------|-----------|----------|---------|
| Weekly deep analysis | 4x | $3 | $12 |
| Daily quick checks | 30x | $0.25 | $7.50 |
| On-demand analyses | 2x | $3 | $6 |
| **Total per client** | | | **$25.50** |

### Optimization Strategies
- Use GPT-3.5-turbo for triage: $0.50 → $0.10 per check
- Cache common patterns: 30% reduction
- Batch multiple clients: 20% reduction
- **Optimized cost: ~$15/client/month**

---

## Next Steps

1. **Validate with AI consultants** - Share this prompt with multiple AIs
2. **Choose architecture** - Based on feedback, select A, B, or C
3. **Build MVP** - Start with core analysis service
4. **Test with Priority Roofing** - Real client data
5. **Iterate** - Refine based on results
6. **Scale** - Add more clients

---

**Decision Point**: Which architecture should we implement?

Share the prompt documents with AIs and gather recommendations before proceeding.

