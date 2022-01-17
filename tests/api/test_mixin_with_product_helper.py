from connect.client import ConnectClient
from connect.processors_toolkit.api.mixins import WithProductHelper


class Helper(WithProductHelper):
    def __init__(self, client: ConnectClient):
        self.client = client


def test_product_helper_should_retrieve_all_product_templates(sync_client_factory, response_factory):
    content = [
        {
            "id": "TL-000-000-001",
            "title": "TPL 1",
            "name": "TPL 1",
            "body": "Template body 1",
            "scope": "asset",
            "position": 80000,
        },
        {
            "id": "TL-000-000-002",
            "title": "TPL 2",
            "name": "TPL 2",
            "body": "Template body 2",
            "scope": "tier1",
            "position": 90000,
        }
    ]

    client = sync_client_factory([
        response_factory(count=len(content), value=content)
    ])

    templates = Helper(client).match_product_templates('PRD-183-233-565', {})

    assert len(templates) == 2


def test_product_helper_should_retrieve_filtered_product_templates(sync_client_factory, response_factory):
    content = [
        {
            "id": "TL-000-000-001",
            "title": "TPL 1",
            "name": "TPL 1",
            "body": "Template body 1",
            "scope": "asset",
            "position": 80000,
        }
    ]

    client = sync_client_factory([
        response_factory(count=len(content), value=content)
    ])

    templates = Helper(client).match_product_templates('PRD-000-000-001', {'scope': 'asset'})

    assert len(templates) == 1
