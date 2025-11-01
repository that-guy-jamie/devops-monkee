#!/usr/bin/env python3
"""
Add negative keywords to the Priority Roofing parallel campaign for efficiency.
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

    # Try broader search for existing ad groups
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

def add_negative_keyword_to_campaign(customer_id: str, campaign_resource_name: str, keyword_text: str, match_type: str):
    """Add a negative keyword to the campaign level."""
    wrapper = GoogleAdsWrapper()

    try:
        # Map match type to enum
        match_type_enum = {
            'Phrase': 'PHRASE',
            'Exact': 'EXACT',
            'Broad': 'BROAD'
        }.get(match_type, 'PHRASE')

        # Create campaign criterion (negative keyword)
        campaign_criterion_service = wrapper.client.get_service("CampaignCriterionService")

        operation = wrapper.client.get_type("CampaignCriterionOperation")
        criterion = operation.create
        criterion.campaign = campaign_resource_name
        criterion.status = wrapper.client.enums.CampaignCriterionStatusEnum.ENABLED
        criterion.negative = True

        # Set negative keyword details
        keyword_info = wrapper.client.get_type("KeywordInfo")
        keyword_info.text = keyword_text
        keyword_info.match_type = getattr(wrapper.client.enums.KeywordMatchTypeEnum, match_type_enum)
        criterion.keyword = keyword_info

        # Execute
        response = campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=[operation]
        )

        print(f"Added campaign-level negative keyword '{keyword_text}' ({match_type})")
        return response.results[0].resource_name

    except Exception as e:
        print(f"Failed to add campaign negative keyword '{keyword_text}': {e}")
        return None

def add_negative_keyword_to_ad_group(customer_id: str, ad_group_resource_name: str, keyword_text: str, match_type: str):
    """Add a negative keyword to an ad group level."""
    wrapper = GoogleAdsWrapper()

    try:
        # Map match type to enum
        match_type_enum = {
            'Phrase': 'PHRASE',
            'Exact': 'EXACT',
            'Broad': 'BROAD'
        }.get(match_type, 'PHRASE')

        # Create ad group criterion (negative keyword)
        ad_group_criterion_service = wrapper.client.get_service("AdGroupCriterionService")

        operation = wrapper.client.get_type("AdGroupCriterionOperation")
        criterion = operation.create
        criterion.ad_group = ad_group_resource_name
        criterion.status = wrapper.client.enums.AdGroupCriterionStatusEnum.ENABLED
        criterion.negative = True

        # Set negative keyword details
        keyword_info = wrapper.client.get_type("KeywordInfo")
        keyword_info.text = keyword_text
        keyword_info.match_type = getattr(wrapper.client.enums.KeywordMatchTypeEnum, match_type_enum)
        criterion.keyword = keyword_info

        # Execute
        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[operation]
        )

        print(f"Added ad group negative keyword '{keyword_text}' ({match_type})")
        return response.results[0].resource_name

    except Exception as e:
        print(f"Failed to add ad group negative keyword '{keyword_text}': {e}")
        return None

def main():
    # Priority Roofing setup
    customer_id = "4139022884"
    campaign_name = "[DRAFT] Priority Roofing - Optimized Parallel"

    print("=" * 60)
    print("ADD NEGATIVE KEYWORDS TO PRIORITY ROOFING CAMPAIGN")
    print("=" * 60)

    # Get campaign resource name
    try:
        campaign_resource_name = get_campaign_resource_name(customer_id, campaign_name)
        print(f"Found campaign: {campaign_resource_name}")
    except Exception as e:
        print(f"Error finding campaign: {e}")
        return

    # Read negative keywords
    negative_keywords_file = "C:/Users/james/Desktop/Projects/Output/priorityroofers.com/pr-roofing_editor_negative_keywords.csv"

    with open(negative_keywords_file, 'r') as f:
        reader = csv.DictReader(f)
        negative_keywords_data = list(reader)

    print(f"\nAdding {len(negative_keywords_data)} negative keywords...")

    # Separate campaign-level and ad group-level negatives
    campaign_negatives = [n for n in negative_keywords_data if n['level'] == 'Campaign']
    ad_group_negatives = [n for n in negative_keywords_data if n['level'] == 'Ad group']

    print(f"Campaign-level negatives: {len(campaign_negatives)}")
    print(f"Ad group-level negatives: {len(ad_group_negatives)}")

    # Add campaign-level negative keywords
    campaign_negative_count = 0
    for neg in campaign_negatives:
        add_negative_keyword_to_campaign(customer_id, campaign_resource_name, neg['Keyword'], neg['Match type'])
        campaign_negative_count += 1

    # Add ad group-level negative keywords
    ad_group_negative_count = 0

    # Group by ad group
    ad_group_negatives_by_group = {}
    for neg in ad_group_negatives:
        ad_group = neg['Ad group']
        if ad_group not in ad_group_negatives_by_group:
            ad_group_negatives_by_group[ad_group] = []
        ad_group_negatives_by_group[ad_group].append(neg)

    for ad_group_name, negatives in ad_group_negatives_by_group.items():
        try:
            ad_group_resource_name = get_ad_group_resource_name(customer_id, campaign_resource_name, ad_group_name)
            print(f"\nAd Group: {ad_group_name}")

            for neg in negatives:
                add_negative_keyword_to_ad_group(customer_id, ad_group_resource_name, neg['Keyword'], neg['Match type'])
                ad_group_negative_count += 1

        except Exception as e:
            print(f"Error processing ad group '{ad_group_name}': {e}")

    print(f"\nNEGATIVE KEYWORD ADDITION COMPLETE!")
    print(f"Added {campaign_negative_count} campaign-level negative keywords")
    print(f"Added {ad_group_negative_count} ad group-level negative keywords")
    print(f"Total: {campaign_negative_count + ad_group_negative_count} negative keywords")
    print("=" * 60)

if __name__ == "__main__":
    main()
