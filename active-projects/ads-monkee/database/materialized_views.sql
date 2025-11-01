-- ============================================================================
-- Materialized Views for AI Analysis
-- ============================================================================
-- These views pre-filter and cap data to keep AI prompts small and cheap.
-- Refresh these views daily or after major data imports.
--
-- Usage:
--   REFRESH MATERIALIZED VIEW focus_keywords_30d;
--   REFRESH MATERIALIZED VIEW focus_search_terms_30d;
-- ============================================================================

-- Drop existing views if they exist
DROP MATERIALIZED VIEW IF EXISTS focus_keywords_30d CASCADE;
DROP MATERIALIZED VIEW IF EXISTS focus_search_terms_30d CASCADE;

-- ============================================================================
-- Focus Keywords (30-day window)
-- ============================================================================
-- Identifies keywords that need attention:
-- 1. Keywords with clicks but CPA > 1.25x target
-- 2. Keywords with spend but zero conversions
-- Capped at 200 rows per client to control token usage.
-- ============================================================================

CREATE MATERIALIZED VIEW focus_keywords_30d AS
WITH keyword_summary AS (
    SELECT
        k.client_id,
        k.campaign_id,
        k.campaign_name,
        k.ad_group_id,
        k.ad_group_name,
        k.keyword_id,
        k.keyword_text,
        k.match_type,
        SUM(k.clicks) AS total_clicks,
        SUM(k.cost) AS total_cost,
        SUM(k.conversions) AS total_conversions,
        AVG(k.quality_score) AS avg_quality_score,
        -- Calculated metrics
        CASE
            WHEN SUM(k.clicks) > 0 THEN SUM(k.cost) / SUM(k.clicks)
            ELSE NULL
        END AS cpc,
        CASE
            WHEN SUM(k.conversions) > 0 THEN SUM(k.cost) / SUM(k.conversions)
            ELSE NULL
        END AS cpa
    FROM agg_keyword_daily k
    WHERE k.date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
),
with_targets AS (
    SELECT
        ks.*,
        t.target_cpa,
        t.target_roas,
        -- Flag problematic keywords
        CASE
            WHEN ks.total_conversions = 0 AND ks.total_cost >= 30 THEN 'high_spend_no_conv'
            WHEN ks.cpa IS NOT NULL AND t.target_cpa IS NOT NULL AND ks.cpa > (t.target_cpa * 1.25) THEN 'high_cpa'
            WHEN ks.avg_quality_score IS NOT NULL AND ks.avg_quality_score < 5 THEN 'low_quality'
            ELSE NULL
        END AS issue_type
    FROM keyword_summary ks
    LEFT JOIN client_targets t ON t.client_id = ks.client_id
)
SELECT
    client_id,
    campaign_id,
    campaign_name,
    ad_group_id,
    ad_group_name,
    keyword_id,
    keyword_text,
    match_type,
    total_clicks,
    total_cost,
    total_conversions,
    avg_quality_score,
    cpc,
    cpa,
    target_cpa,
    issue_type
FROM with_targets
WHERE issue_type IS NOT NULL
    AND total_clicks >= 5  -- Minimum sample size
ORDER BY total_cost DESC
LIMIT 200;

-- Add index for fast lookups
CREATE INDEX idx_focus_keywords_client ON focus_keywords_30d (client_id);
CREATE INDEX idx_focus_keywords_issue ON focus_keywords_30d (issue_type);

-- ============================================================================
-- Focus Search Terms (30-day window)
-- ============================================================================
-- Identifies search terms that should be added as negative keywords:
-- 1. High spend with zero conversions
-- 2. CPA significantly above target
-- Capped at 200 rows to control token usage.
-- ============================================================================

CREATE MATERIALIZED VIEW focus_search_terms_30d AS
WITH search_term_summary AS (
    SELECT
        st.client_id,
        st.campaign_id,
        st.campaign_name,
        st.ad_group_id,
        st.ad_group_name,
        st.search_term,
        st.match_type_delivered,
        SUM(st.clicks) AS total_clicks,
        SUM(st.cost) AS total_cost,
        SUM(st.conversions) AS total_conversions,
        -- Calculated metrics
        CASE
            WHEN SUM(st.clicks) > 0 THEN SUM(st.cost) / SUM(st.clicks)
            ELSE NULL
        END AS cpc,
        CASE
            WHEN SUM(st.conversions) > 0 THEN SUM(st.cost) / SUM(st.conversions)
            ELSE NULL
        END AS cpa
    FROM agg_search_term_daily st
    WHERE st.date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY 1, 2, 3, 4, 5, 6, 7
),
with_targets AS (
    SELECT
        sts.*,
        t.target_cpa,
        -- Flag problematic search terms
        CASE
            WHEN sts.total_conversions = 0 AND sts.total_cost >= 30 THEN 'high_spend_no_conv'
            WHEN sts.cpa IS NOT NULL AND t.target_cpa IS NOT NULL AND sts.cpa > (t.target_cpa * 1.25) THEN 'high_cpa'
            ELSE NULL
        END AS issue_type
    FROM search_term_summary sts
    LEFT JOIN client_targets t ON t.client_id = sts.client_id
)
SELECT
    client_id,
    campaign_id,
    campaign_name,
    ad_group_id,
    ad_group_name,
    search_term,
    match_type_delivered,
    total_clicks,
    total_cost,
    total_conversions,
    cpc,
    cpa,
    target_cpa,
    issue_type
FROM with_targets
WHERE issue_type IS NOT NULL
    AND total_clicks >= 3  -- Minimum sample size
ORDER BY total_cost DESC
LIMIT 200;

-- Add index for fast lookups
CREATE INDEX idx_focus_search_terms_client ON focus_search_terms_30d (client_id);
CREATE INDEX idx_focus_search_terms_issue ON focus_search_terms_30d (issue_type);

-- ============================================================================
-- Refresh Script
-- ============================================================================
-- Run this daily or after data imports:
--
-- REFRESH MATERIALIZED VIEW focus_keywords_30d;
-- REFRESH MATERIALIZED VIEW focus_search_terms_30d;
-- ============================================================================

