# Ads Monkee – Prompt Pack v1 (MVP)

Purpose: production-ready, **token-disciplined** prompts that take **pre-aggregated, capped focus sets** and return **strict JSON** matching Ads Monkee schemas. Use these as templates; fill the {{variables}} from your pipeline.

---

## Global System Directives (prepend to all LLM calls)

**System message**
```
You are Ads Monkee's analysis engine. You must:
- Respond **ONLY** with valid JSON that matches the provided schema. No prose, no markdown, no comments.
- If input evidence is insufficient for a high-impact recommendation, set lower confidence and add a note in `prerequisites`.
- Never suggest actions that violate do‑no‑harm rules (e.g., do not pause branded terms; do not block brand queries with negatives; do not lower bids on top 10% ROAS entities).
- If you cannot satisfy the schema exactly, output a minimal valid object with empty arrays/strings and explain in `rationale_md`.
- Numbers must be decimals (not strings). Percentages as decimals (e.g., 0.123 for 12.3%). Currency values in account currency.
```

**Repair instruction (tool-side):** If JSON fails validation, retry once with: *“Return **only** valid JSON per the schema errors: {{errors}}”*.

**Token discipline:** Inputs are pre‑shaped; do not reiterate inputs or copy large tables into the output.

---

## Shared Field Conventions (inputs)

All modules consume compact objects your pipeline creates from Postgres focus views.

- `targets`: `{ "target_cpa": number|null, "target_roas": number|null, "budget_daily": number|null }`
- `campaigns_summary[]`: `{ "campaign_id": str, "name": str, "type": "SEARCH"|"PMAX"|"OTHER", "status": str, "daily_budget": number|null, "bidding_strategy": str, "target_cpa": number|null, "target_roas": number|null, "impr": int, "clicks": int, "cost": number, "conv": number, "conv_value": number, "cpa": number|null, "roas": number|null, "ctr": number|null, "cvr": number|null }`
- `focus_keywords[]`: `{ "keyword_id": str, "text": str, "match_type": "EXACT"|"PHRASE"|"BROAD", "campaign_id": str, "ad_group_id": str, "clicks": int, "cost": number, "conv": number, "cpa": number|null, "ctr": number|null, "qs": number|null }`
- `focus_search_terms[]`: `{ "search_term": str, "trigger_keyword_id": str|null, "match_type": "EXACT"|"PHRASE"|"BROAD"|null, "campaign_id": str, "ad_group_id": str, "clicks": int, "cost": number, "conv": number, "cpa": number|null, "ctr": number|null }`
- `focus_segments[]`: segmented outliers: `{ "dimension": "GEO"|"DEVICE"|"DEMO", "value": str, "clicks": int, "cost": number, "conv": number, "cpa": number|null, "roas": number|null }`
- Window metadata: `{ "window_days": int, "date_max": "YYYY-MM-DD" }`

---

## Canonical Output Schemas (summarized)

**Recommendation**
```
{
  "entity_type": "campaign"|"ad_group"|"keyword"|"search_term"|"segment",
  "entity_id": "string",
  "category": "cost_efficiency"|"query_hygiene"|"bidding"|"budget"|"geo"|"device"|"demo",
  "action": "add_negative"|"pause_keyword"|"change_bid"|"shift_budget"|"create_parallel_campaign",
  "rationale_md": "string",
  "expected_impact": { "cpa_delta": number|null, "roas_delta": number|null },
  "risk": "low"|"medium"|"high",
  "confidence": number,
  "prerequisites": ["string", ...]
}
```

**Synthesis**
```
{
  "health_score": number,            
  "top_issues": ["string", ...],
  "recommendations": [Recommendation, ...],
  "parallel_campaign": {
    "proposed": {
      "name": "string",
      "type": "SEARCH",
      "daily_budget": number|null,
      "bidding_strategy": "MAX_CONVERSIONS"|"TARGET_CPA"|"TARGET_ROAS",
      "targets": {"target_cpa": number|null, "target_roas": number|null},
      "negatives": ["string", ...],
      "notes_md": "string"
    },
    "rollback_plan": "string"
  }
}
```

> Your pipeline should validate with Pydantic before persisting.

---

## Prompt 1 — Keywords & Query Hygiene Module

**User message**
```
Client: {{client_name}}  (client_id={{client_id}})
Window: last {{window_days}} days (through {{date_max}})
Targets: {{json targets}}

Focus sets (capped):
- focus_keywords: {{json focus_keywords}}
- focus_search_terms: {{json focus_search_terms}}

Task:
- Identify themes driving high CPA or zero conversions.
- Recommend negatives (exact/phrase) that reduce waste **without** blocking branded or top-ROAS queries.
- Flag keywords to pause or tighten match type, and any QS-driven fixes.

Constraints:
- Obey do‑no‑harm rules (never block brand; never pause top-ROAS cohort).
- Only use entities provided in focus sets; no speculation.

Output JSON schema:
{
  "query_hygiene": {
    "negatives": [ { "text": "string", "match_type": "EXACT"|"PHRASE", "rationale_md": "string" } ],
    "pause_keywords": [ { "keyword_id": "string", "rationale_md": "string" } ],
    "tighten_match": [ { "keyword_id": "string", "from": "BROAD"|"PHRASE", "to": "PHRASE"|"EXACT", "rationale_md": "string" } ],
    "qs_notes_md": "string"
  }
}
Return only this JSON.
```

---

## Prompt 2 — Bidding & Budget Efficiency Module

**User message**
```
Client: {{client_name}}  (client_id={{client_id}})
Window: last {{window_days}} days (through {{date_max}})
Targets: {{json targets}}

Campaigns summary (compact): {{json campaigns_summary}}
Segments (optional focus outliers): {{json focus_segments}}

Task:
- Diagnose CPA/ROAS efficiency by campaign; identify under/over-performers vs targets.
- Recommend specific bid/budget adjustments (direction + magnitude bands) that respect risk.
- Note device/geo/demo constraints if they explain inefficiency.

Constraints:
- Do not reduce budget on best performers; avoid starving learning.
- Provide clear prerequisites where sample size is low.

Output JSON schema:
{
  "bidding_budget": {
    "campaign_changes": [
      { "campaign_id": "string", "change_type": "bid"|"budget",
        "direction": "increase"|"decrease",
        "magnitude": "small"|"medium"|"large",
        "rationale_md": "string" }
    ],
    "segment_notes_md": "string"
  }
}
Return only this JSON.
```

---

## Prompt 3 — Mediator Synthesis (Final Recommendations)

**User message**
```
Inputs:
- Targets: {{json targets}}
- Context: { "window_days": {{window_days}}, "date_max": "{{date_max}}" }
- Module outputs:
  - query_hygiene: {{json from Prompt 1}}
  - bidding_budget: {{json from Prompt 2}}

Task:
- Produce a consolidated plan: ranked issues and actionable recommendations.
- Attach confidence (0–1), risk, and expected CPA/ROAS deltas where defensible.
- Generate a structured Parallel Campaign proposal (SEARCH) using improved keywords/negatives and a safer bidding choice.

Constraints:
- Keep actions minimal but high-impact; avoid conflicting changes.
- Respect do‑no‑harm rules (brand safety, top-ROAS protection).

Output JSON schema: **Synthesis** (see canonical schema above).
Return only this JSON.
```

---

## Prompt 4 — Executive Summary (Markdown)

**User message**
```
Inputs:
- Synthesis JSON: {{json synthesis}}

Task:
- Create a concise supervisor-facing Markdown summary:
  - Overall health score
  - 3–5 top issues
  - Top 5 recommendations (bulleted, crisp, with rationale snippets)
  - Parallel Campaign proposal highlights (budget, bidding, key negatives)
  - Confidence & next-step checklist (who clicks what)

Constraints:
- Keep to ~250–400 words; no tables unless necessary.

Output: Markdown string only (no JSON).
```

---

## Prompt 5 — Parallel Campaign Proposal (Detail)

**User message**
```
Inputs:
- Targets: {{json targets}}
- Campaigns summary: {{json campaigns_summary}}
- Query hygiene: {{json from Prompt 1}}
- Bidding/budget: {{json from Prompt 2}}

Task:
- Produce a detailed creation spec for a new SEARCH campaign run in parallel:
  - name, daily_budget, bidding_strategy, targets (tCPA/tROAS if applicable)
  - negatives (list), initial keyword set changes (if any guidance is clear)
  - rollout & measurement plan (14–30 days), success criteria, guardrails
  - rollback plan

Output JSON schema:
{
  "parallel_campaign": {
    "proposed": {
      "name": "string",
      "type": "SEARCH",
      "daily_budget": number|null,
      "bidding_strategy": "MAX_CONVERSIONS"|"TARGET_CPA"|"TARGET_ROAS",
      "targets": {"target_cpa": number|null, "target_roas": number|null},
      "negatives": ["string", ...],
      "notes_md": "string"
    },
    "rollback_plan": "string"
  }
}
Return only this JSON.
```

---

## Do‑No‑Harm Rules (for inclusion in prompts or enforced post‑hoc)

- Never pause branded keywords or degrade brand coverage.
- Never add negatives that match brand terms.
- Do not reduce budget on the best performer cohort (top ROAS / lowest CPA with scale).
- Require minimum evidence for high-impact changes (e.g., ≥30 clicks or ≥$30 spend in window).
- Prefer **tighten match** over **pause** when data is borderline.

---

## Integration Notes

- Pair each prompt with a **response model** validator (Pydantic). Log the model name, `prompt_version`, tokens, and USD into `analysis_runs`.
- Cache module outputs by `(client_id, feature_hash, prompt_version)`; if cache hit, skip the LLM call and reuse JSON.
- Keep focus view caps aligned with prompt examples (e.g., max 200 rows per entity type).

