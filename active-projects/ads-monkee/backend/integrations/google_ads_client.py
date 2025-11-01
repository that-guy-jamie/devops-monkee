from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from google.ads.googleads.client import GoogleAdsClient


@dataclass
class CampaignSnapshot:
    resource_name: str
    id: str
    name: str
    status: str
    advertising_channel_type: str
    bidding_strategy_type: Optional[str]
    daily_budget_micros: int


class GoogleAdsWrapper:
    def __init__(self) -> None:
        # Try to load from google-ads.yaml file first
        try:
            self.client = GoogleAdsClient.load_from_storage("google-ads.yaml")
        except Exception:
            # Fallback to environment variables if YAML file fails
            developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
            client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
            refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
            login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")

            if not all([developer_token, client_id, client_secret, refresh_token]):
                raise RuntimeError("Missing Google Ads credentials in environment or google-ads.yaml")

            config: Dict[str, Any] = {
                "developer_token": developer_token,
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                # Explicitly set login_customer_id when provided to avoid account mismatch
                "login_customer_id": login_customer_id.replace("-", "") if login_customer_id else None,
                # Use default version bundled with the library
            }
            # Remove None keys
            config = {k: v for k, v in config.items() if v is not None}

            self.client = GoogleAdsClient.load_from_dict(config)

    def _ga_service(self):
        return self.client.get_service("GoogleAdsService")

    def _budget_service(self):
        return self.client.get_service("CampaignBudgetService")

    def _campaign_service(self):
        return self.client.get_service("CampaignService")

    def get_active_search_campaign(self, customer_id: str) -> Optional[CampaignSnapshot]:
        ga_service = self._ga_service()
        query = (
            "SELECT campaign.resource_name, campaign.id, campaign.name, campaign.status, "
            "campaign.advertising_channel_type, campaign.bidding_strategy_type, "
            "campaign_budget.amount_micros "
            "FROM campaign "
            "WHERE campaign.status IN ('ENABLED', 'PAUSED') "
            "AND campaign.advertising_channel_type = 'SEARCH' "
            "ORDER BY campaign.status DESC, campaign.id DESC "
            "LIMIT 1"
        )
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            return CampaignSnapshot(
                resource_name=row.campaign.resource_name,
                id=str(row.campaign.id),
                name=row.campaign.name,
                status=row.campaign.status.name,
                advertising_channel_type=row.campaign.advertising_channel_type.name,
                bidding_strategy_type=(row.campaign.bidding_strategy_type.name if row.campaign.bidding_strategy_type else None),
                daily_budget_micros=int(row.campaign_budget.amount_micros),
            )
        return None

    def create_campaign_paused_with_budget(
        self,
        customer_id: str,
        name: str,
        daily_budget_micros: int,
        bidding_strategy_type: Optional[str] = None,
        labels: Optional[list[str]] = None,
    ) -> str:
        budget_service = self._budget_service()
        campaign_service = self._campaign_service()

        budget_operation = self.client.get_type("CampaignBudgetOperation")
        budget = budget_operation.create
        budget.name = f"{name} - Budget"
        budget.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.STANDARD
        budget.amount_micros = daily_budget_micros
        budget.explicitly_shared = False

        budget_response = budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[budget_operation]
        )
        budget_resource_name = budget_response.results[0].resource_name

        campaign_operation = self.client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = name
        campaign.status = self.client.enums.CampaignStatusEnum.PAUSED
        campaign.advertising_channel_type = self.client.enums.AdvertisingChannelTypeEnum.SEARCH
        campaign.campaign_budget = budget_resource_name

        # Set bidding strategy for campaign creation using proper API pattern
        # Based on google-ads-python examples (shopping_ads, app_campaigns)
        # For maximize conversions, set target_cpa_micros to None
        campaign.maximize_conversions.target_cpa_micros = None

        # Set EU political advertising status (required field)
        campaign.contains_eu_political_advertising = (
            self.client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
        )

        if labels:
            campaign.labels.extend(labels)

        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        return campaign_response.results[0].resource_name

    def get_campaign_snapshot(self, customer_id: str, campaign_resource_name: str) -> CampaignSnapshot:
        ga_service = self._ga_service()
        query = (
            "SELECT campaign.resource_name, campaign.id, campaign.name, campaign.status, "
            "campaign.advertising_channel_type, campaign.bidding_strategy_type, "
            "campaign_budget.amount_micros "
            f"FROM campaign WHERE campaign.resource_name = '{campaign_resource_name}'"
        )
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            return CampaignSnapshot(
                resource_name=row.campaign.resource_name,
                id=str(row.campaign.id),
                name=row.campaign.name,
                status=row.campaign.status.name,
                advertising_channel_type=row.campaign.advertising_channel_type.name,
                bidding_strategy_type=(row.campaign.bidding_strategy_type.name if row.campaign.bidding_strategy_type else None),
                daily_budget_micros=int(row.campaign_budget.amount_micros),
            )
        raise RuntimeError("Campaign not found after creation")

    def set_campaign_status(self, customer_id: str, campaign_resource_name: str, status: str) -> None:
        campaign_service = self._campaign_service()
        operation = self.client.get_type("CampaignOperation")
        campaign = operation.update
        campaign.resource_name = campaign_resource_name
        enum_val = getattr(self.client.enums.CampaignStatusEnum, status)
        campaign.status = enum_val
        field_mask = self.client.get_type("FieldMask")
        field_mask.paths.append("status")
        operation.update_mask.CopyFrom(field_mask)
        campaign_service.mutate_campaigns(customer_id=customer_id, operations=[operation])



# Backwards-compatibility shim for earlier code expecting GoogleAdsIntegration
class GoogleAdsIntegration:
    """Lightweight wrapper exposing get_service(), loading config from google-ads.yaml.

    Some scripts assume a class named GoogleAdsIntegration with a get_service() method.
    This shim preserves that interface while allowing env-based config elsewhere.
    """

    def __init__(self) -> None:
        # Prefer local google-ads.yaml if present; fall back to env-based wrapper
        try:
            self.client = GoogleAdsClient.load_from_storage("google-ads.yaml")
        except Exception:
            # Fall back to env-configured wrapper
            self._wrapper = GoogleAdsWrapper()
            self.client = self._wrapper.client

    def get_service(self, service_name: str):
        return self.client.get_service(service_name)

