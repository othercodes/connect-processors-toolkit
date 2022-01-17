from typing import Union

from connect.client import ConnectClient, AsyncConnectClient
from connect.processors_toolkit.requests.tier_configurations import TierConfigurationBuilder

from connect.processors_toolkit.requests.assets import AssetBuilder

from connect.processors_toolkit.api.mixins import WithHelpdeskHelper
from connect.processors_toolkit.requests import RequestBuilder


class Helper(WithHelpdeskHelper):
    def __init__(self, client: Union[ConnectClient, AsyncConnectClient]):
        self.client = client


def test_helper_should_create_a_helpdesk_case(sync_client_factory, response_factory):
    request = RequestBuilder()
    request.with_id('PR-0000-0000-0000-001')

    client = sync_client_factory([
        response_factory(value={
            "id": "CA-000-000-000",
            "subject": "PR-0000-0000-0000-001: The case subject 001.",
            "description": "This is the long description of the case 001.",
            "priority": 0,
            "type": "technical",
            "state": "pending",
            "receiver": {
                "account": {
                    "id": "PA-000-000-000",
                },
            },
        })
    ])

    case = Helper(client).create_helpdesk_case(
        request=request,
        subject="The case subject 001.",
        description="This is the long description of the case 001.",
        receiver_id="PA-000-000-000",
    )

    assert isinstance(case, dict)


def test_helper_should_create_a_helpdesk_case_for_issuer_recipients(sync_client_factory, response_factory):
    request = RequestBuilder()
    request.with_id('PR-0000-0000-0000-001')

    client = sync_client_factory([
        response_factory(value={
            "id": "CA-000-000-000",
            "subject": "PR-0000-0000-0000-001: The case subject 002.",
            "description": "This is the long description of the case 002.",
            "priority": 0,
            "type": "technical",
            "state": "pending",
            "issuer": {
                "recipients": [
                    {"id": "UR-630-250-903"}
                ]
            },
            "receiver": {
                "account": {
                    "id": "PA-000-000-000",
                },
            },
        })
    ])

    case = Helper(client).create_helpdesk_case(
        request=request,
        subject="The case subject 002.",
        description="This is the long description of the case 002.",
        receiver_id="PA-000-000-000",
        issuer_recipients=[
            {"id": "UR-630-250-903"}
        ]
    )

    assert isinstance(case, dict)


def test_helper_should_create_a_helpdesk_case_for_asset_product(sync_client_factory, response_factory):
    request = RequestBuilder()
    request.with_id('PR-0000-0000-0000-001')
    asset = AssetBuilder()
    asset.with_asset_product('PRD-000-000-000')
    request.with_asset(asset)

    client = sync_client_factory([
        response_factory(value={
            "id": "CA-000-000-000",
            "subject": "PR-0000-0000-0000-001: The case subject 003.",
            "description": "This is the long description of the case 003.",
            "priority": 0,
            "type": "technical",
            "state": "pending",
            "product": {
                "id": "PRD-000-000-000",
            },
            "receiver": {
                "account": {
                    "id": "PA-000-000-000",
                },
            },
        })
    ])

    case = Helper(client).create_helpdesk_case(
        request=request,
        subject="The case subject.",
        description="This is the long description of the case 003.",
        receiver_id="PA-000-000-000",
    )

    assert isinstance(case, dict)


def test_helper_should_create_a_helpdesk_case_for_tier_config_product(sync_client_factory, response_factory):
    request = RequestBuilder()
    request.with_id('TCR-0000-0000-0000-001')
    tier = TierConfigurationBuilder()
    tier.with_tier_configuration_product('PRD-000-000-000')
    request.with_tier_configuration(tier)

    client = sync_client_factory([
        response_factory(value={
            "id": "CA-000-000-000",
            "subject": "PR-0000-0000-0000-001: The case subject 004.",
            "description": "This is the long description of the case 004.",
            "priority": 0,
            "type": "technical",
            "state": "pending",
            "product": {
                "id": "PRD-000-000-000",
            },
            "receiver": {
                "account": {
                    "id": "PA-000-000-000",
                },
            },
        })
    ])

    case = Helper(client).create_helpdesk_case(
        request=request,
        subject="The case subject.",
        description="This is the long description of the case 004.",
        receiver_id="PA-000-000-000",
    )

    assert isinstance(case, dict)
