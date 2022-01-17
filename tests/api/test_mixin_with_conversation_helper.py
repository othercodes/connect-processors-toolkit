import pytest

from connect.client import ConnectClient
from connect.processors_toolkit.api.mixins import WithConversationHelper


class Helper(WithConversationHelper):
    def __init__(self, client: ConnectClient):
        self.client = client


def test_conversation_helper_should_retrieve_a_conversation_by_id(sync_client_factory, response_factory):
    on_server = {
        "id": "CO-281-587-907-301-310-717",
        "instance_id": "PR-2434-0591-2885-001",
        "topic": "Fulfillment Request <PR-2434-0591-2885-001>",
        "type": "conversation",
        "status": "open",
        "accounts": [
            {
                "id": "VA-610-138",
                "name": "IMC Alpha Team Vendor"
            }
        ],
        "created": "2022-01-13T09:50:00+00:00"
    }

    client = sync_client_factory([
        response_factory(value=on_server, status=200)
    ])

    conversation = Helper(client).find_conversation('CO-281-587-907-301-310-717')

    assert conversation['id'] == 'CO-281-587-907-301-310-717'


def test_conversation_helper_should_retrieve_conversations_by_criteria_all(sync_client_factory, response_factory):
    on_server = [
        {
            "id": "CO-281-587-907-301-310-717",
            "instance_id": "PR-2434-0591-2885-002",
            "topic": "Fulfillment Request <PR-2434-0591-2885-002>",
            "type": "conversation",
            "status": "open",
            "accounts": [
                {
                    "id": "VA-610-138",
                    "name": "IMC Lambda Team Vendor"
                }
            ],
            "created": "2022-01-13T09:30:00+00:00"
        },
        {
            "id": "CO-281-587-907-301-310-718",
            "instance_id": "PR-2434-0591-2885-003",
            "topic": "Fulfillment Request <PR-2434-0591-2885-003>",
            "type": "conversation",
            "status": "open",
            "accounts": [
                {
                    "id": "VA-610-138",
                    "name": "IMC Omicron Team Vendor"
                }
            ],
            "created": "2022-01-13T09:49:28+00:00"
        }
    ]

    client = sync_client_factory([
        response_factory(value=on_server, status=200, count=len(on_server))
    ])

    conversations = Helper(client).match_conversations({})

    assert len(conversations) == 2


def test_conversation_helper_should_retrieve_conversations_by_criteria(sync_client_factory, response_factory):
    on_server = [
        {
            "id": "CO-281-587-907-301-310-719",
            "instance_id": "PR-2434-0591-2885-008",
            "topic": "Fulfillment Request <PR-2434-0591-2885-008>",
            "type": "conversation",
            "status": "open",
            "accounts": [
                {
                    "id": "VA-610-138",
                    "name": "IMC Gamma Team Vendor"
                }
            ],
            "created": "2022-01-13T09:49:28+00:00"
        }
    ]

    client = sync_client_factory([
        response_factory(value=on_server, status=200)
    ])

    conversations = Helper(client).match_conversations({'id': 'CO-281-587-907-301-310-719'})

    assert len(conversations) == 1


def test_conversation_helper_should_add_a_message_to_a_conversation(sync_client_factory, response_factory):
    on_server = [
        {
            "id": "CO-281-587-907-301-310-717",
            "instance_id": "PR-2434-0591-2885-009",
            "topic": "Fulfillment Request <PR-2434-0591-2885-009>",
            "type": "conversation",
            "status": "open",
            "accounts": [
                {
                    "id": "VA-610-138",
                    "name": "IMC Beta Team Vendor"
                }
            ],
            "created": "2022-01-13T09:30:00+00:00"
        }
    ]

    created_message = {
        "id": "ME-946-723-371-633-205-783",
        "conversation": "CO-281-587-907-301-310-717",
        "account": {
            "id": "VA-610-138",
            "name": "IMC Beta Team Vendor"
        },
        "created": "2022-01-13T11:30:10+00:00",
        "creator": {
            "id": "SU-829-966-028",
            "name": "John Dow"
        },
        "text": "Hello World message!",
        "type": "message",
    }

    client = sync_client_factory([
        response_factory(value=on_server, status=200),
        response_factory(value=created_message, status=200)
    ])

    message = Helper(client).add_conversation_message_by_request_id(
        'PR-2434-0591-2885-009',
        'Hello World message!',
    )

    assert message['text'] == 'Hello World message!'


def test_conversation_helper_should_fail_adding_a_message_to_a_conversation(sync_client_factory, response_factory):
    client = sync_client_factory([
        response_factory(value=[], status=200)
    ])

    with pytest.raises(ValueError):
        Helper(client).add_conversation_message_by_request_id(
            'PR-2434-0591-2885-009',
            'Hello World this message will fail!',
        )
