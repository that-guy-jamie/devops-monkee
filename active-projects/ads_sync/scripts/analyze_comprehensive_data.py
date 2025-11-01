#!/usr/bin/env python3
"""
analyze_comprehensive_data.py - AI-Powered PPC Campaign Analysis & Recommendations

Analyzes comprehensive Google Ads data and generates actionable recommendations
for campaign optimization. Designed for multi-agent consensus building and
integration with GoHighLevel for client reporting.

Features:
- Top expensive search terms analysis
- Low quality score keyword identification
- Negative keyword recommendations
- Budget optimization suggestions
- Ad group performance analysis
- Geographic performance insights
- Device performance breakdown
- Demographic targeting recommendations
- Conversion funnel analysis

Usage:
    python scripts/analyze_comprehensive_data.py --client priority-roofing
    python scripts/analyze_comprehensive_data.py --client priority-roofing --format markdown
    python scripts/analyze_comprehensive_data.py --client priority-roofing --format json --output report.json

Author: OneClickSEO PPC Management
Version: 0.1.0
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import pytz

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


class PPCAnalyzer:
    """Comprehensive PPC campaign analyzer with AI-powered recommendations."""
    
    def __init__(self, client_slug: str, data_timestamp: str = None):
        """
        Initialize analyzer with client data.
        
        Args:
            client_slug: Client slug (e.g., 'priority-roofing')
            data_timestamp: Specific timestamp to analyze (e.g., '20251016_043710')
                           If None, uses most recent data
        """
        self.client_slug = client_slug
        self.data_dir = DATA_DIR / client_slug / "comprehensive"
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"No comprehensive data found for {client_slug}")
        
        # Find data files
        if data_timestamp:
            self.timestamp = data_timestamp
        else:
            # Find most recent timestamp
            files = list(self.data_dir.glob(f"{client_slug}-campaigns-*.csv"))
            if not files:
                raise FileNotFoundError(f"No campaign data found for {client_slug}")
            latest = max(files, key=lambda p: p.stat().st_mtime)
            self.timestamp = latest.stem.split('-')[-1]
        
        # Load all data
        self.campaigns = self._load_data('campaigns')
        self.ad_groups = self._load_data('ad_groups')
        self.keywords = self._load_data('keywords')
        self.search_terms = self._load_data('search_terms')
        self.ads = self._load_data('ads')
        self.geographic = self._load_data('geographic')
        self.device = self._load_data('device')
        self.demographics = self._load_data('demographics')
        
        # Calculate derived metrics
        self._calculate_metrics()
    
    def _load_data(self, data_type: str) -> Optional[pd.DataFrame]:
        """Load a specific data type CSV."""
        file_path = self.data_dir / f"{self.client_slug}-{data_type}-{self.timestamp}.csv"
        
        if not file_path.exists():
            print(f"[WARNING] No {data_type} data found")
            return None
        
        try:
            df = pd.read_csv(file_path)
            print(f"[OK] Loaded {len(df)} rows of {data_type} data")
            return df
        except Exception as e:
            print(f"[ERROR] Failed to load {data_type}: {e}")
            return None
    
    def _calculate_metrics(self):
        """Calculate derived metrics for all dataframes."""
        for df_name in ['campaigns', 'ad_groups', 'keywords', 'search_terms', 'device']:
            df = getattr(self, df_name)
            if df is not None and not df.empty:
                # CTR
                if 'impressions' in df.columns and 'clicks' in df.columns:
                    df['ctr'] = df.apply(
                        lambda row: (row['clicks'] / row['impressions'] * 100) if row['impressions'] > 0 else 0,
                        axis=1
                    )
                
                # CPC (if not already present)
                if 'cost' in df.columns and 'clicks' in df.columns and 'avg_cpc' not in df.columns:
                    df['avg_cpc'] = df.apply(
                        lambda row: row['cost'] / row['clicks'] if row['clicks'] > 0 else 0,
                        axis=1
                    )
                
                # CPA
                if 'cost' in df.columns and 'conversions' in df.columns:
                    df['cpa'] = df.apply(
                        lambda row: row['cost'] / row['conversions'] if row['conversions'] > 0 else None,
                        axis=1
                    )
                
                # Conversion Rate
                if 'clicks' in df.columns and 'conversions' in df.columns:
                    df['conv_rate'] = df.apply(
                        lambda row: (row['conversions'] / row['clicks'] * 100) if row['clicks'] > 0 else 0,
                        axis=1
                    )
    
    def analyze_top_expensive_search_terms(self, top_n: int = 20) -> Dict[str, Any]:
        """
        Identify most expensive search terms and waste analysis.
        
        Returns dict with:
        - top_wasters: High spend, no conversions
        - top_performers: High spend, good ROAS
        - recommendations: Negative keyword suggestions
        """
        if self.search_terms is None or self.search_terms.empty:
            return {"error": "No search terms data available"}
        
        # Aggregate by search term
        st_agg = self.search_terms.groupby('search_term').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'cost': 'sum',
            'conversions': 'sum',
            'conversions_value': 'sum'
        }).reset_index()
        
        # Calculate metrics
        st_agg['ctr'] = (st_agg['clicks'] / st_agg['impressions'] * 100).fillna(0)
        st_agg['avg_cpc'] = (st_agg['cost'] / st_agg['clicks']).fillna(0)
        st_agg['cpa'] = (st_agg['cost'] / st_agg['conversions']).fillna(0).replace([float('inf')], None)
        st_agg['conv_rate'] = (st_agg['conversions'] / st_agg['clicks'] * 100).fillna(0)
        st_agg['roas'] = (st_agg['conversions_value'] / st_agg['cost']).fillna(0).replace([float('inf')], 0)
        
        # Top wasters: High spend, no conversions
        wasters = st_agg[
            (st_agg['cost'] > 10) & (st_agg['conversions'] == 0)
        ].sort_values('cost', ascending=False).head(top_n)
        
        # Top performers: High spend, good conversions
        performers = st_agg[
            (st_agg['cost'] > 10) & (st_agg['conversions'] > 0)
        ].sort_values('cost', ascending=False).head(top_n)
        
        # Low CTR terms (potential quality issues)
        low_ctr = st_agg[
            (st_agg['impressions'] > 100) & (st_agg['ctr'] < 1.0)
        ].sort_values('cost', ascending=False).head(top_n)
        
        return {
            "top_wasters": wasters.to_dict('records'),
            "top_performers": performers.to_dict('records'),
            "low_ctr_terms": low_ctr.to_dict('records'),
            "total_wasted_spend": float(wasters['cost'].sum()),
            "total_analyzed_terms": len(st_agg),
            "recommendations": self._generate_negative_keyword_recommendations(wasters)
        }
    
    def _generate_negative_keyword_recommendations(self, wasters_df: pd.DataFrame) -> List[str]:
        """Generate negative keyword recommendations from waster terms."""
        recommendations = []
        
        for _, row in wasters_df.head(10).iterrows():
            term = row['search_term']
            cost = row['cost']
            clicks = row['clicks']
            
            recommendations.append(
                f"Add '{term}' as negative keyword (wasted ${cost:.2f} on {int(clicks)} clicks with 0 conversions)"
            )
        
        return recommendations
    
    def analyze_low_quality_keywords(self, threshold: int = 5) -> Dict[str, Any]:
        """
        Identify keywords with low quality scores.
        
        Args:
            threshold: Quality score threshold (default: 5)
        
        Returns analysis with improvement recommendations
        """
        if self.keywords is None or self.keywords.empty:
            return {"error": "No keywords data available"}
        
        # Filter for keywords with quality scores
        kw_with_qs = self.keywords[self.keywords['quality_score'].notna()].copy()
        
        if kw_with_qs.empty:
            return {"error": "No quality score data available"}
        
        # Aggregate by keyword
        kw_agg = kw_with_qs.groupby(['keyword_text', 'match_type']).agg({
            'quality_score': 'first',  # QS doesn't change daily
            'creative_quality': 'first',
            'landing_page_quality': 'first',
            'expected_ctr': 'first',
            'impressions': 'sum',
            'clicks': 'sum',
            'cost': 'sum',
            'conversions': 'sum',
            'max_cpc_bid': 'mean'
        }).reset_index()
        
        # Low quality keywords
        low_quality = kw_agg[kw_agg['quality_score'] <= threshold].sort_values('cost', ascending=False)
        
        # Quality score distribution
        qs_distribution = kw_agg.groupby('quality_score').agg({
            'keyword_text': 'count',
            'cost': 'sum',
            'conversions': 'sum'
        }).rename(columns={'keyword_text': 'keyword_count'})
        
        return {
            "low_quality_keywords": low_quality.to_dict('records'),
            "total_low_quality": len(low_quality),
            "wasted_on_low_quality": float(low_quality['cost'].sum()),
            "quality_score_distribution": qs_distribution.to_dict('index'),
            "avg_quality_score": float(kw_agg['quality_score'].mean()),
            "recommendations": self._generate_quality_score_recommendations(low_quality)
        }
    
    def _generate_quality_score_recommendations(self, low_quality_df: pd.DataFrame) -> List[str]:
        """Generate recommendations for improving quality scores."""
        recommendations = []
        
        for _, row in low_quality_df.head(10).iterrows():
            keyword = row['keyword_text']
            qs = row['quality_score']
            cost = row['cost']
            
            issues = []
            if row['creative_quality'] in ['BELOW_AVERAGE', 'AVERAGE']:
                issues.append("improve ad copy relevance")
            if row['landing_page_quality'] in ['BELOW_AVERAGE', 'AVERAGE']:
                issues.append("optimize landing page")
            if row['expected_ctr'] in ['BELOW_AVERAGE', 'AVERAGE']:
                issues.append("improve ad CTR")
            
            if issues:
                rec = f"'{keyword}' (QS: {qs}) - ${cost:.2f} spent - {', '.join(issues)}"
            else:
                rec = f"'{keyword}' (QS: {qs}) - ${cost:.2f} spent - Review ad relevance and landing page experience"
            
            recommendations.append(rec)
        
        return recommendations
    
    def analyze_budget_optimization(self) -> Dict[str, Any]:
        """Analyze budget allocation and provide optimization recommendations."""
        if self.campaigns is None or self.campaigns.empty:
            return {"error": "No campaign data available"}
        
        # Aggregate by campaign
        camp_agg = self.campaigns.groupby('campaign_name').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'cost': 'sum',
            'conversions': 'sum',
            'conversions_value': 'sum',
            'impression_share': 'mean',
            'budget_lost_is': 'mean',
            'rank_lost_is': 'mean'
        }).reset_index()
        
        # Calculate metrics
        camp_agg['ctr'] = (camp_agg['clicks'] / camp_agg['impressions'] * 100).fillna(0)
        camp_agg['cpa'] = (camp_agg['cost'] / camp_agg['conversions']).replace([float('inf')], None)
        camp_agg['conv_rate'] = (camp_agg['conversions'] / camp_agg['clicks'] * 100).fillna(0)
        camp_agg['roas'] = (camp_agg['conversions_value'] / camp_agg['cost']).fillna(0).replace([float('inf')], 0)
        
        # Budget-limited campaigns (high budget lost IS)
        budget_limited = camp_agg[camp_agg['budget_lost_is'] > 0.1].sort_values('budget_lost_is', ascending=False)
        
        # Underperforming campaigns
        underperforming = camp_agg[
            (camp_agg['cost'] > 100) & 
            ((camp_agg['conversions'] == 0) | (camp_agg['cpa'] > camp_agg['cpa'].median()))
        ].sort_values('cost', ascending=False)
        
        # High performers
        top_performers = camp_agg[
            (camp_agg['conversions'] > 0) & (camp_agg['roas'] > 1.0)
        ].sort_values('roas', ascending=False)
        
        return {
            "campaign_performance": camp_agg.to_dict('records'),
            "budget_limited_campaigns": budget_limited.to_dict('records'),
            "underperforming_campaigns": underperforming.to_dict('records'),
            "top_performing_campaigns": top_performers.to_dict('records'),
            "total_spend": float(camp_agg['cost'].sum()),
            "total_conversions": float(camp_agg['conversions'].sum()),
            "avg_cpa": float(camp_agg['cpa'].mean()) if not camp_agg['cpa'].isna().all() else None,
            "overall_roas": float(camp_agg['conversions_value'].sum() / camp_agg['cost'].sum()) if camp_agg['cost'].sum() > 0 else 0,
            "recommendations": self._generate_budget_recommendations(camp_agg, budget_limited, underperforming, top_performers)
        }
    
    def _generate_budget_recommendations(
        self, 
        all_campaigns: pd.DataFrame,
        budget_limited: pd.DataFrame,
        underperforming: pd.DataFrame,
        top_performers: pd.DataFrame
    ) -> List[str]:
        """Generate budget reallocation recommendations."""
        recommendations = []
        
        # Increase budgets for limited campaigns
        for _, row in budget_limited.head(3).iterrows():
            budget_lost = row['budget_lost_is'] * 100
            campaign = row['campaign_name']
            recommendations.append(
                f"INCREASE budget for '{campaign}' - losing {budget_lost:.1f}% impression share due to budget"
            )
        
        # Decrease or pause underperformers
        for _, row in underperforming.head(3).iterrows():
            campaign = row['campaign_name']
            cost = row['cost']
            conversions = row['conversions']
            
            if conversions == 0:
                recommendations.append(
                    f"PAUSE or reduce '{campaign}' - ${cost:.2f} spent with 0 conversions"
                )
            else:
                cpa = row['cpa']
                recommendations.append(
                    f"REDUCE budget for '{campaign}' - High CPA: ${cpa:.2f}"
                )
        
        # Reallocate to top performers
        for _, row in top_performers.head(3).iterrows():
            campaign = row['campaign_name']
            roas = row['roas']
            recommendations.append(
                f"INCREASE budget for '{campaign}' - Strong ROAS: {roas:.2f}x"
            )
        
        return recommendations
    
    def analyze_device_performance(self) -> Dict[str, Any]:
        """Analyze performance by device type."""
        if self.device is None or self.device.empty:
            return {"error": "No device data available"}
        
        # Aggregate by device
        device_agg = self.device.groupby('device').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'cost': 'sum',
            'conversions': 'sum',
            'conversions_value': 'sum'
        }).reset_index()
        
        # Calculate metrics
        device_agg['ctr'] = (device_agg['clicks'] / device_agg['impressions'] * 100).fillna(0)
        device_agg['avg_cpc'] = (device_agg['cost'] / device_agg['clicks']).fillna(0)
        device_agg['cpa'] = (device_agg['cost'] / device_agg['conversions']).replace([float('inf')], None)
        device_agg['conv_rate'] = (device_agg['conversions'] / device_agg['clicks'] * 100).fillna(0)
        device_agg['roas'] = (device_agg['conversions_value'] / device_agg['cost']).fillna(0).replace([float('inf')], 0)
        device_agg['cost_pct'] = (device_agg['cost'] / device_agg['cost'].sum() * 100)
        device_agg['conv_pct'] = (device_agg['conversions'] / device_agg['conversions'].sum() * 100).fillna(0)
        
        return {
            "device_performance": device_agg.to_dict('records'),
            "recommendations": self._generate_device_recommendations(device_agg)
        }
    
    def _generate_device_recommendations(self, device_agg: pd.DataFrame) -> List[str]:
        """Generate device bid adjustment recommendations."""
        recommendations = []
        
        # Find best/worst performing devices
        if not device_agg.empty and 'conv_rate' in device_agg.columns:
            best_device = device_agg.loc[device_agg['conv_rate'].idxmax()]
            worst_device = device_agg.loc[device_agg['conv_rate'].idxmin()]
            
            if best_device['conv_rate'] > worst_device['conv_rate'] * 1.5:
                recommendations.append(
                    f"INCREASE bids for {best_device['device']} - Conv Rate: {best_device['conv_rate']:.2f}% vs {worst_device['device']}: {worst_device['conv_rate']:.2f}%"
                )
                recommendations.append(
                    f"DECREASE bids for {worst_device['device']} - Underperforming with {worst_device['conv_rate']:.2f}% conversion rate"
                )
            
            # Mobile-specific recommendations
            mobile_data = device_agg[device_agg['device'] == 'MOBILE']
            if not mobile_data.empty:
                mobile_conv = mobile_data.iloc[0]['conv_rate']
                mobile_cost_pct = mobile_data.iloc[0]['cost_pct']
                
                if mobile_conv < device_agg['conv_rate'].mean():
                    recommendations.append(
                        f"Review mobile landing page experience - Mobile conv rate ({mobile_conv:.2f}%) below average"
                    )
                
                if mobile_cost_pct > 60:
                    recommendations.append(
                        f"Mobile accounts for {mobile_cost_pct:.1f}% of spend - Ensure mobile optimization is priority"
                    )
        
        return recommendations
    
    def analyze_geographic_performance(self) -> Dict[str, Any]:
        """Analyze performance by geographic location."""
        if self.geographic is None or self.geographic.empty:
            return {"error": "No geographic data available"}
        
        # Aggregate by region (state/province)
        geo_agg = self.geographic.groupby('region').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'cost': 'sum',
            'conversions': 'sum',
            'conversions_value': 'sum'
        }).reset_index()
        
        # Remove null regions
        geo_agg = geo_agg[geo_agg['region'].notna()]
        
        if geo_agg.empty:
            return {"error": "No valid geographic data"}
        
        # Calculate metrics
        geo_agg['ctr'] = (geo_agg['clicks'] / geo_agg['impressions'] * 100).fillna(0)
        geo_agg['cpa'] = (geo_agg['cost'] / geo_agg['conversions']).replace([float('inf')], None)
        geo_agg['conv_rate'] = (geo_agg['conversions'] / geo_agg['clicks'] * 100).fillna(0)
        geo_agg['roas'] = (geo_agg['conversions_value'] / geo_agg['cost']).fillna(0).replace([float('inf')], 0)
        
        # Sort by spend
        geo_agg = geo_agg.sort_values('cost', ascending=False)
        
        return {
            "top_regions": geo_agg.head(20).to_dict('records'),
            "recommendations": self._generate_geographic_recommendations(geo_agg)
        }
    
    def _generate_geographic_recommendations(self, geo_agg: pd.DataFrame) -> List[str]:
        """Generate geographic targeting recommendations."""
        recommendations = []
        
        if geo_agg.empty:
            return recommendations
        
        # Top performing regions
        top_regions = geo_agg[geo_agg['conversions'] > 0].sort_values('roas', ascending=False).head(5)
        for _, row in top_regions.iterrows():
            recommendations.append(
                f"INCREASE bids in {row['region']} - ROAS: {row['roas']:.2f}x, Conv Rate: {row['conv_rate']:.2f}%"
            )
        
        # High spend, low conversion regions
        wasters = geo_agg[(geo_agg['cost'] > 100) & (geo_agg['conversions'] == 0)].head(5)
        for _, row in wasters.iterrows():
            recommendations.append(
                f"EXCLUDE or reduce bids in {row['region']} - ${row['cost']:.2f} spent with 0 conversions"
            )
        
        return recommendations
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate complete analysis report with all insights and recommendations."""
        print("\n[ANALYSIS] Generating comprehensive report...")
        
        report = {
            "client": self.client_slug,
            "report_date": datetime.now(pytz.UTC).isoformat(),
            "data_timestamp": self.timestamp,
            "data_range": self._get_date_range(),
            "executive_summary": {},
            "search_terms_analysis": {},
            "quality_score_analysis": {},
            "budget_optimization": {},
            "device_performance": {},
            "geographic_performance": {},
            "recommendations": {
                "high_priority": [],
                "medium_priority": [],
                "low_priority": []
            }
        }
        
        # Executive summary
        print("[ANALYSIS] Calculating executive summary...")
        report["executive_summary"] = self._generate_executive_summary()
        
        # Search terms analysis
        print("[ANALYSIS] Analyzing search terms...")
        report["search_terms_analysis"] = self.analyze_top_expensive_search_terms()
        
        # Quality score analysis
        print("[ANALYSIS] Analyzing quality scores...")
        report["quality_score_analysis"] = self.analyze_low_quality_keywords()
        
        # Budget optimization
        print("[ANALYSIS] Analyzing budget allocation...")
        report["budget_optimization"] = self.analyze_budget_optimization()
        
        # Device performance
        print("[ANALYSIS] Analyzing device performance...")
        report["device_performance"] = self.analyze_device_performance()
        
        # Geographic performance
        print("[ANALYSIS] Analyzing geographic performance...")
        report["geographic_performance"] = self.analyze_geographic_performance()
        
        # Consolidate and prioritize recommendations
        print("[ANALYSIS] Consolidating recommendations...")
        report["recommendations"] = self._prioritize_all_recommendations(report)
        
        print("[ANALYSIS] Report generation complete!\n")
        return report
    
    def _get_date_range(self) -> Dict[str, str]:
        """Get date range from campaign data."""
        if self.campaigns is not None and not self.campaigns.empty:
            return {
                "start_date": str(self.campaigns['date'].min()),
                "end_date": str(self.campaigns['date'].max()),
                "days": len(self.campaigns['date'].unique())
            }
        return {}
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """Generate high-level executive summary."""
        summary = {
            "total_spend": 0,
            "total_conversions": 0,
            "total_revenue": 0,
            "overall_roas": 0,
            "avg_cpa": 0,
            "avg_ctr": 0,
            "total_clicks": 0,
            "total_impressions": 0,
            "wasted_spend": 0,
            "optimization_potential": 0
        }
        
        if self.campaigns is not None and not self.campaigns.empty:
            summary["total_spend"] = float(self.campaigns['cost'].sum())
            summary["total_conversions"] = float(self.campaigns['conversions'].sum())
            summary["total_revenue"] = float(self.campaigns['conversions_value'].sum())
            summary["total_clicks"] = int(self.campaigns['clicks'].sum())
            summary["total_impressions"] = int(self.campaigns['impressions'].sum())
            
            if summary["total_spend"] > 0:
                summary["overall_roas"] = summary["total_revenue"] / summary["total_spend"]
            
            if summary["total_conversions"] > 0:
                summary["avg_cpa"] = summary["total_spend"] / summary["total_conversions"]
            
            if summary["total_impressions"] > 0:
                summary["avg_ctr"] = (summary["total_clicks"] / summary["total_impressions"]) * 100
        
        # Calculate wasted spend (from search terms with no conversions)
        if self.search_terms is not None and not self.search_terms.empty:
            wasted = self.search_terms[self.search_terms['conversions'] == 0]
            summary["wasted_spend"] = float(wasted['cost'].sum())
            summary["optimization_potential"] = (summary["wasted_spend"] / summary["total_spend"] * 100) if summary["total_spend"] > 0 else 0
        
        return summary
    
    def _prioritize_all_recommendations(self, report: Dict[str, Any]) -> Dict[str, List[str]]:
        """Consolidate and prioritize all recommendations."""
        high_priority = []
        medium_priority = []
        low_priority = []
        
        # High priority: Budget waste and underperformers
        if "search_terms_analysis" in report and "recommendations" in report["search_terms_analysis"]:
            high_priority.extend(report["search_terms_analysis"]["recommendations"][:5])
        
        if "budget_optimization" in report and "underperforming_campaigns" in report["budget_optimization"]:
            underperf = report["budget_optimization"]["underperforming_campaigns"]
            if underperf:
                high_priority.append(f"Review {len(underperf)} underperforming campaigns - ${sum(c['cost'] for c in underperf):.2f} at risk")
        
        # Medium priority: Quality scores and device optimization
        if "quality_score_analysis" in report and "recommendations" in report["quality_score_analysis"]:
            medium_priority.extend(report["quality_score_analysis"]["recommendations"][:5])
        
        if "device_performance" in report and "recommendations" in report["device_performance"]:
            medium_priority.extend(report["device_performance"]["recommendations"])
        
        # Low priority: Geographic and budget increases
        if "budget_optimization" in report and "recommendations" in report["budget_optimization"]:
            budget_recs = report["budget_optimization"]["recommendations"]
            increase_recs = [r for r in budget_recs if "INCREASE" in r]
            low_priority.extend(increase_recs[:3])
        
        if "geographic_performance" in report and "recommendations" in report["geographic_performance"]:
            low_priority.extend(report["geographic_performance"]["recommendations"][:5])
        
        return {
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority
        }


def format_report_markdown(report: Dict[str, Any], client_name: str = None) -> str:
    """Format analysis report as markdown."""
    md = []
    
    # Header
    md.append(f"# PPC Campaign Analysis Report")
    md.append(f"")
    if client_name:
        md.append(f"**Client:** {client_name}")
    md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"**Data Period:** {report['data_range']['start_date']} to {report['data_range']['end_date']} ({report['data_range']['days']} days)")
    md.append(f"")
    md.append("---")
    md.append("")
    
    # Executive Summary
    md.append("## Executive Summary")
    md.append("")
    summary = report["executive_summary"]
    md.append(f"- **Total Spend:** ${summary['total_spend']:,.2f}")
    md.append(f"- **Total Conversions:** {summary['total_conversions']:.0f}")
    md.append(f"- **Total Revenue:** ${summary['total_revenue']:,.2f}")
    md.append(f"- **Overall ROAS:** {summary['overall_roas']:.2f}x")
    md.append(f"- **Average CPA:** ${summary['avg_cpa']:.2f}")
    md.append(f"- **Average CTR:** {summary['avg_ctr']:.2f}%")
    md.append(f"- **Wasted Spend:** ${summary['wasted_spend']:,.2f} ({summary['optimization_potential']:.1f}% of total)")
    md.append("")
    md.append("---")
    md.append("")
    
    # High Priority Recommendations
    md.append("## 🔴 High Priority Recommendations")
    md.append("")
    for i, rec in enumerate(report["recommendations"]["high_priority"], 1):
        md.append(f"{i}. {rec}")
    md.append("")
    md.append("---")
    md.append("")
    
    # Search Terms Analysis
    md.append("## Search Terms Analysis")
    md.append("")
    st_analysis = report["search_terms_analysis"]
    if "error" not in st_analysis:
        md.append(f"**Total Wasted Spend:** ${st_analysis['total_wasted_spend']:,.2f}")
        md.append(f"**Total Search Terms Analyzed:** {st_analysis['total_analyzed_terms']:,}")
        md.append("")
        
        md.append("### Top 10 Wasting Search Terms")
        md.append("")
        md.append("| Search Term | Cost | Clicks | Conversions |")
        md.append("|-------------|------|--------|-------------|")
        for term in st_analysis["top_wasters"][:10]:
            md.append(f"| {term['search_term']} | ${term['cost']:.2f} | {int(term['clicks'])} | {int(term['conversions'])} |")
        md.append("")
    md.append("---")
    md.append("")
    
    # Quality Score Analysis
    md.append("## Quality Score Analysis")
    md.append("")
    qs_analysis = report["quality_score_analysis"]
    if "error" not in qs_analysis:
        md.append(f"**Average Quality Score:** {qs_analysis['avg_quality_score']:.1f}")
        md.append(f"**Low Quality Keywords:** {qs_analysis['total_low_quality']}")
        md.append(f"**Spend on Low Quality:** ${qs_analysis['wasted_on_low_quality']:,.2f}")
        md.append("")
    md.append("---")
    md.append("")
    
    # Budget Optimization
    md.append("## Budget Optimization")
    md.append("")
    budget = report["budget_optimization"]
    if "error" not in budget:
        md.append("### Campaign Performance")
        md.append("")
        md.append("| Campaign | Spend | Conversions | CPA | ROAS |")
        md.append("|----------|-------|-------------|-----|------|")
        for camp in budget["campaign_performance"][:10]:
            cpa_str = f"${camp['cpa']:.2f}" if camp['cpa'] else "N/A"
            md.append(f"| {camp['campaign_name']} | ${camp['cost']:.2f} | {camp['conversions']:.0f} | {cpa_str} | {camp['roas']:.2f}x |")
        md.append("")
    md.append("---")
    md.append("")
    
    # Device Performance
    md.append("## Device Performance")
    md.append("")
    device = report["device_performance"]
    if "error" not in device:
        md.append("| Device | Impressions | Clicks | Cost | Conv Rate | ROAS |")
        md.append("|--------|-------------|--------|------|-----------|------|")
        for dev in device["device_performance"]:
            md.append(f"| {dev['device']} | {int(dev['impressions']):,} | {int(dev['clicks']):,} | ${dev['cost']:.2f} | {dev['conv_rate']:.2f}% | {dev['roas']:.2f}x |")
        md.append("")
    md.append("---")
    md.append("")
    
    # All Recommendations
    md.append("## All Recommendations")
    md.append("")
    md.append("### 🔴 High Priority")
    for i, rec in enumerate(report["recommendations"]["high_priority"], 1):
        md.append(f"{i}. {rec}")
    md.append("")
    
    md.append("### 🟡 Medium Priority")
    for i, rec in enumerate(report["recommendations"]["medium_priority"], 1):
        md.append(f"{i}. {rec}")
    md.append("")
    
    md.append("### 🟢 Low Priority")
    for i, rec in enumerate(report["recommendations"]["low_priority"], 1):
        md.append(f"{i}. {rec}")
    md.append("")
    
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze comprehensive Google Ads data and generate recommendations'
    )
    parser.add_argument(
        '--client',
        type=str,
        required=True,
        help='Client slug (e.g., priority-roofing)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'markdown', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (optional, defaults to output/{client}/)'
    )
    parser.add_argument(
        '--timestamp',
        type=str,
        help='Specific data timestamp to analyze (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        print(f"\n[INIT] Initializing analyzer for {args.client}...")
        analyzer = PPCAnalyzer(args.client, args.timestamp)
        
        # Generate full report
        report = analyzer.generate_full_report()
        
        # Prepare output directory
        if args.output:
            output_path = Path(args.output)
        else:
            output_dir = OUTPUT_DIR / args.client
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = output_dir / f"analysis-report-{timestamp}"
        
        # Save outputs
        if args.format in ['json', 'both']:
            json_path = output_path.with_suffix('.json')
            with open(json_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n[OK] JSON report saved to: {json_path}")
        
        if args.format in ['markdown', 'both']:
            md_path = output_path.with_suffix('.md')
            md_content = format_report_markdown(report, args.client)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"[OK] Markdown report saved to: {md_path}")
        
        # Print summary to console
        print("\n" + "=" * 80)
        print("ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Client: {args.client}")
        print(f"Total Spend: ${report['executive_summary']['total_spend']:,.2f}")
        print(f"Total Conversions: {report['executive_summary']['total_conversions']:.0f}")
        print(f"Overall ROAS: {report['executive_summary']['overall_roas']:.2f}x")
        print(f"Wasted Spend: ${report['executive_summary']['wasted_spend']:,.2f}")
        print(f"Optimization Potential: {report['executive_summary']['optimization_potential']:.1f}%")
        print("=" * 80)
        print(f"\nTop 5 High Priority Recommendations:")
        for i, rec in enumerate(report['recommendations']['high_priority'][:5], 1):
            print(f"{i}. {rec}")
        print("\n")
        
        return 0
    
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

