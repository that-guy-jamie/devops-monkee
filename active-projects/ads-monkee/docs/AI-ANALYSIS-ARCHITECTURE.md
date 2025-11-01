# Ads Monkee — AI Analysis Architecture (Modified Plan)

## 0) Executive Summary

* **MVP Architecture:** Start with **Option A (Standalone)** for speed and reliability, designed to evolve seamlessly to **Option C (Hybrid)**.
* **Engine:** FastAPI + **Celery/Redis** + PostgreSQL. Web returns **202** immediately; workers do all heavy lifting.
* **Analysis Style:** **Staged pipeline** with aggressive SQL pre-aggregation → focused LLM modules → mediator-style synthesis.
* **Models (MVP):** **Single model** (Claude 3.5 Sonnet or GPT-4 Turbo) for all stages with **strict JSON validation** (Pydantic).
* **Outputs:** **Structured JSON is canonical**; human Markdown derived from it.
* **GHL (MVP):** **Minimal**—notify + optional re-run trigger. Approvals happen in Ads Monkee.
* **Cost:** Token caps via **focus/materialized views**, caching by feature hash, per-client budgets.
* **Roadmap:** After launch, add schedules, event triggers, tiered models, and (optionally) multi-agent consensus.

---

## 1) Target Architecture

```
Google Ads → Postgres (raw + aggregates + focus views)
                  │
           Celery/Redis (orchestration)
                  │
         FastAPI "Analysis Service"
    ┌─────────────┴──────────────┐
Supervisor UI (React)        GHL (notify, trigger)
```

* **MVP = Option A:** All approvals/actions in Ads Monkee.
* **V2 = Option C:** Push summaries + approval tasks to GHL; keep engine in-house.

---

## 2) Core Components

* **PostgreSQL:** Source of truth. Raw tables + **agg*** (daily) + **focus*** (materialized) + results tables.
* **FastAPI:**

  * `POST /clients/{id}/analyze` → enqueue and return **202** with `run_id`.
  * `GET /analysis/{run_id}` → status + JSON + Markdown.
* **Celery + Redis:** Chains tasks; per-client concurrency=1; rate limits protect quotas.
* **LLM Adapter:** Single model (MVP) with Pydantic validation+auto-repair (e.g., `instructor`-style).

---

## 3) Data Layer (make AI cheap)

Create persistent, token-capped, repeatable sources:

* **Aggregates:**

  * `agg_campaign_daily`, `agg_adgroup_daily`, `agg_keyword_daily`, `agg_search_term_daily`, `agg_geo_device_demo` (30/90d windows).
  * `targets` (client CPA/ROAS goals, budgets).

* **Focus (materialized) views:** cap rows to keep prompts small.

  * `focus_keywords_30d` (≥ clicks; CPA > 1.25× target or spenders with 0 conv).
  * `focus_search_terms_30d` (top N cost with 0 conv / poor CPA).
  * `focus_segments_30d` (geo/device/demo outliers).

**Example (token guard):**

```sql
create materialized view if not exists focus_search_terms_30d as
with st as (
  select client_id, search_term, sum(clicks) c, sum(cost) cost, sum(conversions) conv
  from agg_search_term_daily
  where date >= current_date - interval '30 day'
  group by 1,2
)
select *
from st
where (conv = 0 and cost >= 30)
   or (conv > 0 and (cost/nullif(conv,0)) >
       (select target_cpa from targets t where t.client_id = st.client_id) * 1.25)
order by cost desc
limit 200;
```

---

## 4) Orchestration (Celery)

* **MVP Trigger:** On-demand "Analyze" button.
* **v1.1:** Add **weekly** comprehensive run (Mon 07:00 local).
* **v2:** Quiet **event-driven spot checks** (CPA spike, CR drop) with debouncing.

**DAG (MVP):**

1. `prepare_data_task` → build compact context from **focus views** + aggregates.
2. `modules_task` → run **keywords/queries** and **bidding/budget** modules (single model).
3. `synthesis_task` → merge module outputs; produce ranked recommendations + parallel campaign proposal.
4. `persist_task` → store JSON + Markdown, costs, prompt versions; notify.

Per-client concurrency=1; idempotent on `(client_id, period, prompt_version)`.

---

## 5) Model Strategy

* **MVP:** One strong model (Claude Sonnet / GPT-4 Turbo) for all stages; **strict JSON** enforced with Pydantic.
* **v2:** Tiered—cheap triage model + strong synthesis.
* **v3 (optional):** Multi-agent (Optimizer / Conservative + Mediator) where ROI justifies.

---

## 6) API Contracts

* `POST /clients/{id}/analyze` → **202** `{ run_id }`
* `GET /analysis/{run_id}` →

  ```json
  {
    "status": "queued|running|done|error",
    "json": { ... },      // only when done
    "markdown": "## ...", // only when done
    "cost": {"input_tokens":1234,"output_tokens":987,"usd":0.42}
  }
  ```

---

## 7) Output (canonical JSON) & Tables

**Pydantic (essentials):**

```python
from pydantic import BaseModel, Field
from typing import Literal, List, Dict

class Recommendation(BaseModel):
    entity_type: Literal["campaign","ad_group","keyword","search_term","segment"]
    entity_id: str
    category: Literal["cost_efficiency","query_hygiene","bidding","budget","geo","device","demo"]
    action: Literal["add_negative","pause_keyword","change_bid","shift_budget","create_parallel_campaign"]
    rationale_md: str
    expected_impact: Dict[str, float] = Field(default_factory=dict)
    risk: Literal["low","medium","high"] = "medium"
    confidence: float = 0.65
    prerequisites: List[str] = []

class Synthesis(BaseModel):
    health_score: float
    top_issues: List[str]
    recommendations: List[Recommendation]
    parallel_campaign: Dict  # structured proposal
```

**DB:**

* `analysis_runs` (run_id, client_id, window, model, prompt_version, token_cost, started_at, finished_at, status, error)
* `analysis_reports` (run_id, json, markdown, health_score, created_at)
* `recommendations` (normalized by rec; FK to run_id)
* `decisions` (approve/reject/by whom/when)
* `actions_executed` (diffs, API status)

Cache by **feature hash** + `prompt_version` to skip re-runs.

---

## 8) Celery Tasks (skeleton)

```python
# tasks.py
from celery import chain, shared_task

@shared_task
def prepare_data_task(client_id, window_days=30):
    # SELECT from materialized views + aggregates, cap rows
    return build_context_from_views(client_id, window_days)  # dict

@shared_task
def analyze_keywords_and_queries(ctx):
    return llm_json("keyword_query_prompt", {"focus": ctx["focus"]})

@shared_task
def analyze_bidding(ctx):
    return llm_json("bidding_prompt", {"summary": ctx["campaigns_summary"]})

@shared_task
def synthesize_task(ctx, mod_kwq, mod_bid):
    payload = {"context": ctx, "modules": {"kwq": mod_kwq, "bid": mod_bid}}
    return llm_json("mediator_prompt", payload)

@shared_task
def persist_task(client_id, run_id, synthesis):
    persist_run(client_id, run_id, synthesis)
    notify_supervisor(client_id, run_id)
    return {"ok": True}

def run_full_analysis(client_id, run_id, window_days=30):
    return chain(
        prepare_data_task.s(client_id, window_days),
        analyze_keywords_and_queries.s(),
        analyze_bidding.s(),
        synthesize_task.s(),
        persist_task.s(client_id, run_id)
    )()
```

**LLM adapter (strict JSON):**

```python
# llm.py
from instructor import from_openai
from openai import OpenAI
from schemas import Synthesis

client = from_openai(OpenAI())

def llm_json(prompt_name: str, data: dict) -> dict:
    # Build compact prompt from focus views; keep under token caps
    res = client.chat.completions.create(
        model="gpt-4o-mini",  # or Claude Sonnet via your adapter
        response_model=Synthesis,
        messages=[
            {"role":"system","content":"Respond ONLY with valid JSON per schema."},
            {"role":"user","content":build_prompt(prompt_name, data)}
        ],
        max_tokens=1800
    )
    return res.model_dump()
```

**FastAPI entrypoint:**

```python
# api.py
from fastapi import APIRouter
from uuid import uuid4
from .tasks import run_full_analysis

router = APIRouter()

@router.post("/clients/{client_id}/analyze", status_code=202)
def analyze(client_id: str):
    run_id = str(uuid4())
    run_full_analysis.delay(client_id=client_id, run_id=run_id, window_days=30)
    return {"run_id": run_id, "status": "queued"}
```

---

## 9) GHL Integration Strategy

* **MVP (minimal):**

  * Send a **webhook/Note**: "Analysis complete for {client}. View in Ads Monkee: {link}."
  * Optional: GHL → Ads Monkee **re-analyze** trigger.

* **V2 (hybrid):**

  * Push **summary** into GHL custom fields.
  * Create GHL tasks per recommendation; approvals post back via webhook → execute in Ads Monkee.
  * Maintain `ghl_sync_state` per recommendation.

---

## 10) Triggers (evolution)

* **MVP:** Manual runs only.
* **v1.1:** Weekly comprehensive run (Mon 07:00 local).
* **v2:** Event-driven:

  * CPA > target × 1.3 with ≥ N clicks (3-day window)
  * Spend surge > M% DoD
  * CR drop > K% with significance
    Debounce + hysteresis to limit noise.

---

## 11) Cost Controls

* **Focus views** (row caps) + compact prompts.
* **Delta-only** runs when possible (analyze changes since last run).
* **Per-client weekly budget** (e.g., $10/week hard cap); fail closed.
* **Cache** by `(feature_hash, prompt_version)`; serve cached if unchanged.
* **Single model MVP**; add tiering after launch.

---

## 12) Scalability on Render

* **Services:**

  * `ads-monkee-api` (FastAPI)
  * `ads-monkee-worker` (Celery)
  * `redis` (Key-Value)
  * `postgres` (managed DB)
* **Scale path:**

  * Horizontal scale **workers** first.
  * Vertical bump **Postgres** when aggregates grow.
  * Keep per-client concurrency=1 for safety.

---

## 13) Implementation Timeline (2–4 Weeks)

**Week 1 – Skeleton**

* Wire Celery/Redis; deploy worker & API (202 pattern).
* Create aggregates + **focus materialized views** + `targets`.
* Define Pydantic schemas; `analysis_runs` & `analysis_reports` tables.

**Week 2 – Brain**

* Build `prepare_data_task` (SQL-only).
* Implement two modules (KW/queries, Bidding) with **strict JSON**.
* Implement `synthesis_task` → JSON + Markdown.

**Week 3 – UI & Actions**

* Supervisor UI: client list → run detail → report (JSON + Markdown).
* "Approve" pipeline maps JSON → actionable diffs (dry run).
* Persist token/cost metrics; add `prompt_version`.

**Week 4 – Harden & Notify**

* Add **weekly schedule**.
* GHL minimal notification + optional re-run trigger.
* Guardrails (never pause brand; minimum sample thresholds).
* Launch.

---

## 14) Risks & Mitigations

* **Token creep:** enforce hard row limits in focus views + assert before LLM calls.
* **Invalid JSON:** Pydantic validation + auto-repair retries; log failures.
* **Quota/Rate:** per-client concurrency=1 + rate limits; backoff.
* **UX stall:** show task phases (prep → modules → synth → done).
* **Sync drift:** store `prompt_version`, model, cost, feature hash per run.

---

## 15) Nice-to-Have (post-launch)

* **Tiered model strategy** (cheap triage, strong synthesis).
* **Event-driven spot checks** with debouncing.
* **Multi-agent mediator** for high-stakes accounts.
* **Confidence scoring** (data sufficiency, historical win-rate, inter-agent agreement).
* **Rollback playbooks** for each action.

---

### TL;DR

Ship a **standalone MVP** with a **staged Celery pipeline**, **focus views**, **single model** with **strict JSON**, **202 API**, and **minimal GHL notifications**. After launch, layer in weekly schedules, tiered models, event triggers, and (optionally) multi-agent consensus—without changing the core contracts.

