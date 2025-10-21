import httpx, os
from typing import Dict, Any

API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

def _pick(obj, keys):
    return {k: obj.get(k) for k in keys if k in obj}

def run_pagespeed(url: str, api_key: str, strategy: str = "mobile") -> Dict[str, Any]:
    """
    Calls the PageSpeed Insights v5 API and returns a simplified result.
    """
    params = {
        "url": url,
        "category": "PERFORMANCE",
        "strategy": strategy,
        "key": api_key
    }
    r = httpx.get(API_URL, params=params, timeout=60.0)
    r.raise_for_status()
    data = r.json()

    # Extract lab (Lighthouse) scores
    lh = data.get("lighthouseResult", {}) or {}
    cats = lh.get("categories", {}) or {}
    perf_score = None
    if "performance" in cats and "score" in cats["performance"]:
        perf_score = int(round((cats["performance"]["score"] or 0) * 100))

    audits = lh.get("audits", {}) or {}
    lcp = audits.get("largest-contentful-paint", {}).get("numericValue")
    cls = audits.get("cumulative-layout-shift", {}).get("numericValue")
    inp = (audits.get("interactive", {}) or {}).get("numericValue")  # INP is not always present in lab; interactive as proxy

    # Field (CrUX) if available
    field = data.get("loadingExperience") or data.get("originLoadingExperience") or {}
    metrics = field.get("metrics", {}) or {}
    field_lcp = (metrics.get("LCP") or metrics.get("LARGEST_CONTENTFUL_PAINT_MS") or {}).get("percentile")
    field_cls = (metrics.get("CLS") or metrics.get("CUMULATIVE_LAYOUT_SHIFT_SCORE") or {}).get("percentile")
    field_inp = (metrics.get("INP") or metrics.get("INTERACTION_TO_NEXT_PAINT") or {}).get("percentile")

    return {
        "performance": perf_score,
        "lab": {
            "LCP": lcp,
            "INP_or_interactive": inp,
            "CLS": cls
        },
        "field": {
            "LCP_pctl": field_lcp,
            "INP_pctl": field_inp,
            "CLS_pctl": field_cls
        },
        "raw": _pick(data, ["id", "analysisUTCTimestamp"])
    }
