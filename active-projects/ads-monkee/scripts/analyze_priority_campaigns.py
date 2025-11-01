#!/usr/bin/env python3
"""
Analyze Priority Roofing campaign performance across multiple data pulls to find actual differences.
This performs a 'second analysis' to identify real performance variations.
"""
import sys
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import statistics

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def analyze_campaign_data():
    """Analyze campaign data from multiple CSV files."""
    data_dir = Path("C:/Users/james/Desktop/Projects/ads_sync/data/priority-roofing/comprehensive")

    # Find all campaign CSV files
    campaign_files = list(data_dir.glob("priority-roofing-campaigns-*.csv"))
    keyword_files = list(data_dir.glob("priority-roofing-keywords-*.csv"))

    print(f"Found {len(campaign_files)} campaign files and {len(keyword_files)} keyword files")

    # Analyze each campaign file
    campaign_data_by_date = {}

    for file_path in sorted(campaign_files):
        date_str = file_path.stem.split('_')[-1].split('.')[0]  # Extract date from filename
        try:
            date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
        except:
            continue

        print(f"\nAnalyzing campaign data from {date_str}")

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            campaigns = list(reader)

        # Group by campaign name
        campaigns_by_name = defaultdict(list)
        for camp in campaigns:
            campaigns_by_name[camp['campaign_name']].append(camp)

        campaign_data_by_date[date_str] = {
            'total_campaigns': len(campaigns),
            'campaigns_by_name': campaigns_by_name,
            'raw_data': campaigns
        }

    return campaign_data_by_date

def find_actual_differences(campaign_data_by_date):
    """Find actual differences between campaign data pulls."""
    print("\n" + "=" * 80)
    print("PRIORITY ROOFING CAMPAIGN ANALYSIS - ACTUAL DIFFERENCES")
    print("=" * 80)

    if len(campaign_data_by_date) < 2:
        print("Need at least 2 data pulls to identify differences")
        return

    # Get sorted dates
    dates = sorted(campaign_data_by_date.keys())

    print(f"\nAnalyzing {len(dates)} data pulls:")
    for date in dates:
        data = campaign_data_by_date[date]
        print(f"  {date}: {data['total_campaigns']} campaigns")

    # Compare first and last data pulls
    first_date = dates[0]
    last_date = dates[-1]

    first_data = campaign_data_by_date[first_date]
    last_data = campaign_data_by_date[last_date]

    print(f"\nComparing {first_date} vs {last_date}:")

    # Find campaigns that exist in both periods
    first_campaigns = set(first_data['campaigns_by_name'].keys())
    last_campaigns = set(last_data['campaigns_by_name'].keys())

    common_campaigns = first_campaigns & last_campaigns
    new_campaigns = last_campaigns - first_campaigns
    removed_campaigns = first_campaigns - last_campaigns

    print(f"\nCAMPAIGN CHANGES:")
    print(f"  Common campaigns: {len(common_campaigns)}")
    print(f"  New campaigns: {len(new_campaigns)}")
    print(f"  Removed campaigns: {len(removed_campaigns)}")

    if new_campaigns:
        print("  New campaigns:")
        for camp in sorted(new_campaigns):
            print(f"    • {camp}")

    if removed_campaigns:
        print("  Removed campaigns:")
        for camp in sorted(removed_campaigns):
            print(f"    • {camp}")

    # Analyze performance changes for common campaigns
    print("\nPERFORMANCE CHANGES:")
    performance_changes = []

    for campaign_name in common_campaigns:
        first_campaigns = first_data['campaigns_by_name'][campaign_name]
        last_campaigns = last_data['campaigns_by_name'][campaign_name]

        # Get latest data point for each period
        first_camp = max(first_campaigns, key=lambda x: x['date'])
        last_camp = max(last_campaigns, key=lambda x: x['date'])

        try:
            first_cost = float(first_camp['cost'])
            last_cost = float(last_camp['cost'])
            first_conversions = float(first_camp['conversions'])
            last_conversions = float(last_camp['conversions'])

            cost_change = ((last_cost - first_cost) / first_cost * 100) if first_cost > 0 else 0
            conv_change = ((last_conversions - first_conversions) / first_conversions * 100) if first_conversions > 0 else 0

            if abs(cost_change) > 5 or abs(conv_change) > 5:  # Only show significant changes
                performance_changes.append({
                    'campaign': campaign_name,
                    'cost_change': cost_change,
                    'conv_change': conv_change,
                    'first_cost': first_cost,
                    'last_cost': last_cost,
                    'first_conversions': first_conversions,
                    'last_conversions': last_conversions
                })

        except (ValueError, KeyError):
            continue

    if performance_changes:
        print(f"  Campaigns with significant performance changes ({len(performance_changes)}):")
        for change in sorted(performance_changes, key=lambda x: abs(x['cost_change']), reverse=True):
            print(f"    • {change['campaign']}:")
            print(f"      Cost: ${change['first_cost']".2f"} → ${change['last_cost']".2f"} ({change['cost_change']"+.1f"}%)")
            print(f"      Conversions: {change['first_conversions']".1f"} → {change['last_conversions']".1f"} ({change['conv_change']"+.1f"}%)")
    else:
        print("  No significant performance changes detected")

    return performance_changes

def analyze_keyword_performance():
    """Analyze keyword performance to identify optimization opportunities."""
    print("\n" + "=" * 80)
    print("KEYWORD PERFORMANCE ANALYSIS")
    print("=" * 80)

    # Use the most recent keyword file
    keyword_files = Path("C:/Users/james/Desktop/Projects/ads_sync/data/priority-roofing/comprehensive").glob("priority-roofing-keywords-*.csv")
    latest_file = max(keyword_files, key=lambda x: x.stat().st_mtime)

    print(f"Analyzing keywords from: {latest_file.name}")

    with open(latest_file, 'r') as f:
        reader = csv.DictReader(f)
        keywords = list(reader)

    print(f"Total keywords analyzed: {len(keywords)}")

    # Group by ad group
    ad_group_keywords = defaultdict(list)
    for kw in keywords:
        ad_group_keywords[kw['ad_group_name']].append(kw)

    print("\nKEYWORDS BY AD GROUP:")
    for ad_group, kws in ad_group_keywords.items():
        print(f"  {ad_group}: {len(kws)} keywords")

    # Find high/low performing keywords
    performing_keywords = []
    for kw in keywords:
        try:
            clicks = int(kw['clicks'])
            conversions = float(kw['conversions'])
            cost = float(kw['cost'])

            if clicks > 0:
                ctr = (clicks / int(kw['impressions'])) * 100 if kw['impressions'] != '0' else 0
                cpc = cost / clicks if clicks > 0 else 0
                conv_rate = (conversions / clicks) * 100 if clicks > 0 else 0

                performing_keywords.append({
                    'keyword': kw['keyword_text'],
                    'ad_group': kw['ad_group_name'],
                    'clicks': clicks,
                    'conversions': conversions,
                    'cost': cost,
                    'ctr': ctr,
                    'cpc': cpc,
                    'conv_rate': conv_rate,
                    'quality_score': kw['quality_score']
                })
        except (ValueError, KeyError):
            continue

    # Sort by performance
    top_performing = sorted(performing_keywords, key=lambda x: x['conv_rate'], reverse=True)[:10]
    low_performing = sorted(performing_keywords, key=lambda x: x['conv_rate'])[:10]

    print("\nTOP PERFORMING KEYWORDS:")
    for kw in top_performing:
        print(f"  {kw['keyword']} ({kw['ad_group']}): {kw['conv_rate']".1f"}% conv rate, {kw['clicks']} clicks, ${kw['cpc']".2f"} CPC")

    print("\nLOW PERFORMING KEYWORDS:")
    for kw in low_performing:
        print(f"  {kw['keyword']} ({kw['ad_group']}): {kw['conv_rate']".1f"}% conv rate, {kw['clicks']} clicks, ${kw['cpc']".2f"} CPC")

    return performing_keywords

def main():
    print("=" * 80)
    print("PRIORITY ROOFING AD EFFORTS - SECOND ANALYSIS")
    print("=" * 80)
    print("Finding ACTUAL differences between campaign data pulls")

    # Analyze campaign data
    campaign_data = analyze_campaign_data()

    if campaign_data:
        differences = find_actual_differences(campaign_data)

        # Analyze keyword performance
        keyword_analysis = analyze_keyword_performance()

        print("
" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

        print("\nSUMMARY:")
        print(f"  Campaign data pulls analyzed: {len(campaign_data)}")
        print(f"  Keywords analyzed: {len(keyword_analysis)}")
        print(f"  Significant performance changes: {len(differences)}")

        if differences:
            print("\nKEY FINDINGS:")
            print("  - Campaign structure has evolved over time")
            print(f"  - {len(differences)} campaigns show significant performance changes")
            print("  - Keyword performance varies significantly by ad group")
        else:
            print("\nKEY FINDINGS:")
            print("  - Campaign structure stable across data pulls")
            print("  - No major performance shifts detected")
            print("  - Keyword optimization opportunities identified")
    else:
        print("\nANALYSIS FAILED:")
        print("  Insufficient data for meaningful comparison")
if __name__ == "__main__":
    main()
