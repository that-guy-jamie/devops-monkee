#!/usr/bin/env python3
"""
Analyze actual performance numbers from Priority Roofing keyword data.
"""
import csv
from pathlib import Path

def analyze_performance():
    """Analyze the real performance numbers."""
    # Find the latest keyword file
    keyword_files = list(Path("C:/Users/james/Desktop/Projects/ads_sync/data/priority-roofing/comprehensive").glob("priority-roofing-keywords-*.csv"))
    latest_file = max(keyword_files, key=lambda x: x.stat().st_mtime)

    print(f"Analyzing performance from: {latest_file.name}")

    with open(latest_file, 'r') as f:
        reader = csv.DictReader(f)
        keywords = list(reader)

    print(f"Total keywords analyzed: {len(keywords)}")

    # Calculate overall metrics
    total_impressions = sum(int(kw['impressions']) for kw in keywords if kw['impressions'] != '')
    total_clicks = sum(int(kw['clicks']) for kw in keywords if kw['clicks'] != '')
    total_cost = sum(float(kw['cost']) for kw in keywords if kw['cost'] != '')
    total_conversions = sum(float(kw['conversions']) for kw in keywords if kw['conversions'] != '')

    if total_clicks > 0:
        ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
        cpc = total_cost / total_clicks
        conv_rate = (total_conversions / total_clicks) * 100 if total_clicks > 0 else 0
    else:
        ctr = 0
        cpc = 0
        conv_rate = 0

    print("\nOVERALL PERFORMANCE METRICS:")
    print(f"  Impressions: {total_impressions:,}")
    print(f"  Clicks: {total_clicks:,}")
    print(f"  CTR: {ctr:.2f}%")
    print(f"  Total Cost: ${total_cost:.2f}")
    print(f"  Average CPC: ${cpc:.2f}")
    print(f"  Conversions: {total_conversions:.1f}")
    print(f"  Conversion Rate: {conv_rate:.2f}%")

    # Analyze performance by ad group
    ad_group_metrics = {}
    for kw in keywords:
        ad_group = kw['ad_group_name']
        if ad_group not in ad_group_metrics:
            ad_group_metrics[ad_group] = {
                'impressions': 0,
                'clicks': 0,
                'cost': 0,
                'conversions': 0
            }

        try:
            ad_group_metrics[ad_group]['impressions'] += int(kw['impressions'])
            ad_group_metrics[ad_group]['clicks'] += int(kw['clicks'])
            ad_group_metrics[ad_group]['cost'] += float(kw['cost'])
            ad_group_metrics[ad_group]['conversions'] += float(kw['conversions'])
        except (ValueError, KeyError):
            continue

    print("\nPERFORMANCE BY AD GROUP:")
    for ad_group, metrics in ad_group_metrics.items():
        if metrics['clicks'] > 0:
            ctr = (metrics['clicks'] / metrics['impressions']) * 100 if metrics['impressions'] > 0 else 0
            cpc = metrics['cost'] / metrics['clicks']
            conv_rate = (metrics['conversions'] / metrics['clicks']) * 100 if metrics['clicks'] > 0 else 0

            print(f"  {ad_group}:")
            print(f"    Impressions: {metrics['impressions']:,}")
            print(f"    Clicks: {metrics['clicks']:,}")
            print(f"    CTR: {ctr:.2f}%")
            print(f"    Cost: ${metrics['cost']:.2f}")
            print(f"    CPC: ${cpc:.2f}")
            print(f"    Conversions: {metrics['conversions']:.1f}")
            print(f"    Conv Rate: {conv_rate:.2f}%")

    # Find top and bottom performing keywords
    performing_keywords = []
    for kw in keywords:
        try:
            clicks = int(kw['clicks'])
            conversions = float(kw['conversions'])
            cost = float(kw['cost'])

            if clicks > 0:
                ctr = (clicks / int(kw['impressions'])) * 100 if kw['impressions'] != '0' else 0
                cpc = cost / clicks
                conv_rate = (conversions / clicks) * 100 if clicks > 0 else 0

                performing_keywords.append({
                    'keyword': kw['keyword_text'],
                    'ad_group': kw['ad_group_name'],
                    'clicks': clicks,
                    'conversions': conversions,
                    'cost': cost,
                    'ctr': ctr,
                    'cpc': cpc,
                    'conv_rate': conv_rate
                })
        except (ValueError, KeyError):
            continue

    # Sort by conversion rate
    top_performing = sorted(performing_keywords, key=lambda x: x['conv_rate'], reverse=True)[:10]
    low_performing = sorted(performing_keywords, key=lambda x: x['conv_rate'])[:10]

    print("\nTOP 10 PERFORMING KEYWORDS:")
    for i, kw in enumerate(top_performing, 1):
        print(f"  {i}. {kw['keyword']} ({kw['ad_group']}): {kw['conv_rate']:.1f}% conv rate, {kw['clicks']} clicks, ${kw['cpc']:.2f} CPC")

    print("\nBOTTOM 10 PERFORMING KEYWORDS:")
    for i, kw in enumerate(low_performing, 1):
        print(f"  {i}. {kw['keyword']} ({kw['ad_group']}): {kw['conv_rate']:.1f}% conv rate, {kw['clicks']} clicks, ${kw['cpc']:.2f} CPC")

    return {
        'overall': {
            'impressions': total_impressions,
            'clicks': total_clicks,
            'ctr': ctr,
            'cost': total_cost,
            'cpc': cpc,
            'conversions': total_conversions,
            'conv_rate': conv_rate
        },
        'ad_groups': ad_group_metrics,
        'top_keywords': top_performing,
        'low_keywords': low_performing
    }

def main():
    print("=" * 80)
    print("PRIORITY ROOFING CAMPAIGN - ACTUAL PERFORMANCE ANALYSIS")
    print("=" * 80)
    print("Looking at the REAL numbers, not just structure...")

    performance_data = analyze_performance()

    print("\n" + "=" * 80)
    print("PERFORMANCE ASSESSMENT")
    print("=" * 80)

    overall = performance_data['overall']

    # Assess performance
    if overall['conv_rate'] < 2:
        print("CONVERSION RATE: POOR (< 2%)")
        print("  - Current rate is below industry standards for roofing")
        print("  - Need significant optimization")
    elif overall['conv_rate'] < 5:
        print("CONVERSION RATE: BELOW AVERAGE (2-5%)")
        print("  - Room for improvement")
    else:
        print("CONVERSION RATE: GOOD (> 5%)")

    if overall['cpc'] > 10:
        print("CPC: HIGH (>$10)")
        print("  - Cost per click is elevated")
    elif overall['cpc'] > 5:
        print("CPC: MODERATE ($5-10)")
    else:
        print("CPC: GOOD (<$5)")

    print(f"\nOverall Assessment: {overall['conv_rate']:.1f}% conversion rate with ${overall['cpc']:.2f} CPC")

    print("\nRECOMMENDATIONS:")
    print("  - Focus on high-converting keywords from the top performers")
    print("  - Pause or optimize low-converting keywords")
    print("  - Consider bid adjustments based on ad group performance")
    print("  - The parallel campaign should target the top-performing ad groups")

if __name__ == "__main__":
    main()
