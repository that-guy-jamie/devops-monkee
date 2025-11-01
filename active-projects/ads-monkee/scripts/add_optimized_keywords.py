#!/usr/bin/env python3
"""
Add optimized keywords to the Priority Roofing parallel campaign.
"""
import sys
import csv
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsWrapper

def get_campaign_resource_name(customer_id: str, campaign_name: str) -> str:
    """Get the resource name for a campaign."""
    wrapper = GoogleAdsWrapper()

    service = wrapper._ga_service()
    query = f"""
    SELECT campaign.resource_name
    FROM campaign
    WHERE campaign.name = '{campaign_name}'
    LIMIT 1
    """

    response = service.search(customer_id=customer_id, query=query)

    for row in response:
        return row.campaign.resource_name

    raise RuntimeError(f"Campaign '{campaign_name}' not found")

def get_ad_group_resource_name(customer_id: str, campaign_resource_name: str, ad_group_name: str) -> str:
    """Get the resource name for an ad group."""
    wrapper = GoogleAdsWrapper()

    service = wrapper._ga_service()
    query = f"""
    SELECT ad_group.resource_name
    FROM ad_group
    WHERE ad_group.campaign = '{campaign_resource_name}'
    AND ad_group.name = '{ad_group_name}'
    LIMIT 1
    """

    response = service.search(customer_id=customer_id, query=query)

    for row in response:
        return row.ad_group.resource_name

    # If not found, it might be the "Roof Repairs" ad group that already exists
    # Let's try a broader search
    broader_query = f"""
    SELECT ad_group.resource_name
    FROM ad_group
    WHERE ad_group.campaign = '{campaign_resource_name}'
    AND ad_group.name LIKE '%{ad_group_name}%'
    LIMIT 1
    """

    response = service.search(customer_id=customer_id, query=broader_query)

    for row in response:
        print(f"Found existing ad group: {row.ad_group.resource_name}")
        return row.ad_group.resource_name

    raise RuntimeError(f"Ad group '{ad_group_name}' not found in campaign")

def add_keyword_to_ad_group(customer_id: str, ad_group_resource_name: str, keyword_text: str, match_type: str):
    """Add a keyword to an ad group."""
    wrapper = GoogleAdsWrapper()

    try:
        # Map match type to enum
        match_type_enum = {
            'Exact': 'EXACT',
            'Phrase': 'PHRASE',
            'Broad': 'BROAD'
        }.get(match_type, 'EXACT')

        # Create ad group criterion (keyword)
        ad_group_criterion_service = wrapper.client.get_service("AdGroupCriterionService")

        operation = wrapper.client.get_type("AdGroupCriterionOperation")
        criterion = operation.create
        criterion.ad_group = ad_group_resource_name
        criterion.status = wrapper.client.enums.AdGroupCriterionStatusEnum.ENABLED

        # Set keyword details
        keyword_info = wrapper.client.get_type("KeywordInfo")
        keyword_info.text = keyword_text
        keyword_info.match_type = getattr(wrapper.client.enums.KeywordMatchTypeEnum, match_type_enum)
        criterion.keyword = keyword_info

        # Execute
        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[operation]
        )

        print(f"Added keyword '{keyword_text}' ({match_type}) to ad group")
        return response.results[0].resource_name

    except Exception as e:
        print(f"Failed to add keyword '{keyword_text}': {e}")
        return None

def main():
    # Priority Roofing setup
    customer_id = "4139022884"
    campaign_name = "[DRAFT] Priority Roofing - Optimized Parallel"

    print("=" * 60)
    print("ADD OPTIMIZED KEYWORDS TO PRIORITY ROOFING CAMPAIGN")
    print("=" * 60)

    # Get campaign resource name
    try:
        campaign_resource_name = get_campaign_resource_name(customer_id, campaign_name)
        print(f"Found campaign: {campaign_resource_name}")
    except Exception as e:
        print(f"Error finding campaign: {e}")
        return

    # Read keywords to add
    keywords_file = "C:/Users/james/Desktop/Projects/Output/priorityroofers.com/pr-roofing_editor_keywords_to_add.csv"

    with open(keywords_file, 'r') as f:
        reader = csv.DictReader(f)
        keywords_data = list(reader)

    print(f"\nAdding {len(keywords_data)} optimized keywords...")

    # Group keywords by ad group
    ad_group_keywords = {}
    for row in keywords_data:
        ad_group = row['Ad group']
        if ad_group not in ad_group_keywords:
            ad_group_keywords[ad_group] = []
        ad_group_keywords[ad_group].append({
            'keyword': row['Keyword'],
            'match_type': row['Match type']
        })

    # Add keywords to each ad group
    total_added = 0
    for ad_group_name, keywords in ad_group_keywords.items():
        try:
            ad_group_resource_name = get_ad_group_resource_name(customer_id, campaign_resource_name, ad_group_name)
            print(f"\nAd Group: {ad_group_name}")

            for kw in keywords:
                add_keyword_to_ad_group(customer_id, ad_group_resource_name, kw['keyword'], kw['match_type'])
                total_added += 1

        except Exception as e:
            print(f"Error processing ad group '{ad_group_name}': {e}")

    print(f"\nKEYWORD ADDITION COMPLETE!")
    print(f"Added {total_added} keywords across {len(ad_group_keywords)} ad groups")
    print("=" * 60)

if __name__ == "__main__":
    main()
