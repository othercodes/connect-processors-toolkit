import pytest

import os

from connect.client import ConnectClient, ClientError
from connect.devops_testing import asserts
from connect.processors_toolkit.requests.tier_configurations import TierConfigurationBuilder

from connect.processors_toolkit.requests import RequestBuilder
from connect.processors_toolkit.api.mixins import WithTierConfigurationHelper


class Helper(WithTierConfigurationHelper):
    def __init__(self, client: ConnectClient):
        self.client = client


BAD_REQUEST_400 = "400 Bad Request"
ASSET_REQUEST_FILE = '/asset_request.json'
TIER_CONFIG_REQUEST_FILE = '/tier_configuration_request.json'


def test_helper_should_retrieve_a_tier_configuration_by_id(sync_client_factory, response_factory):
    tier_on_server = TierConfigurationBuilder()
    tier_on_server.with_tier_configuration_id('TC-9091-4850-9712')

    client = sync_client_factory([
        response_factory(value=tier_on_server.raw(), status=200)
    ])

    tc = Helper(client).find_tier_configuration('TC-9091-4850-9712')

    assert isinstance(tc, TierConfigurationBuilder)
    assert tc.tier_configuration_id() == 'TC-9091-4850-9712'


def test_helper_should_match_all_tier_configurations(sync_client_factory, response_factory):
    content = [
        TierConfigurationBuilder({'id': 'TC-000-000-001'}).raw(),
        TierConfigurationBuilder({'id': 'TC-000-000-002'}).raw()
    ]

    client = sync_client_factory([
        response_factory(count=len(content), value=content)
    ])

    templates = Helper(client).match_tier_configuration({})

    assert len(templates) == 2


def test_helper_should_match_tier_configurations(sync_client_factory, response_factory):
    content = [
        TierConfigurationBuilder({'id': 'TC-000-000-001'}).raw(),
    ]

    client = sync_client_factory([
        response_factory(count=len(content), value=content)
    ])

    templates = Helper(client).match_tier_configuration({'id': 'TC-000-000-001'})

    assert len(templates) == 1


def test_helper_should_retrieve_a_tier_configuration_request_by_id(sync_client_factory, response_factory):
    tier_on_server = TierConfigurationBuilder()
    tier_on_server.with_tier_configuration_id('TC-9091-4850-9712')

    on_server = RequestBuilder()
    on_server.with_id('TCR-9091-4850-9712-001')
    on_server.with_type('setup')
    on_server.with_status('pending')
    on_server.with_tier_configuration(tier_on_server)

    client = sync_client_factory([
        response_factory(value=on_server.raw(), status=200)
    ])

    request = Helper(client).find_tier_configuration_request('TCR-9091-4850-9712-001')

    assert isinstance(request, RequestBuilder)
    assert request.id() == 'TCR-9091-4850-9712-001'


def test_helper_should_match_all_tier_configuration_requests(sync_client_factory, response_factory):
    content = [
        RequestBuilder({'id': 'TCR-000-000-001-001'}).raw(),
        RequestBuilder({'id': 'TCR-000-000-002-002'}).raw()
    ]

    client = sync_client_factory([
        response_factory(count=len(content), value=content)
    ])

    templates = Helper(client).match_tier_configuration_request({})

    assert len(templates) == 2


def test_helper_should_match_tier_configuration_requests(sync_client_factory, response_factory):
    content = [
        RequestBuilder({'id': 'TCR-000-000-001-001'}).raw(),
    ]

    client = sync_client_factory([
        response_factory(count=len(content), value=content)
    ])

    templates = Helper(client).match_tier_configuration_request({'id': 'TCR-000-000-001-001'})

    assert len(templates) == 1


def test_helper_should_approve_a_tier_configuration_request(sync_client_factory, response_factory):
    tier_on_server = TierConfigurationBuilder()
    tier_on_server.with_tier_configuration_id('TC-8027-7606-7082')
    tier_on_server.with_tier_configuration_status('active')

    on_server = RequestBuilder()
    on_server.with_id('TCR-8027-7606-7082-001')
    on_server.with_type('setup')
    on_server.with_status('approved')
    on_server.with_tier_configuration(tier_on_server)

    client = sync_client_factory([
        response_factory(value=on_server.raw(), status=200)
    ])

    tier = on_server.tier_configuration()
    tier.with_tier_configuration_status('processing')

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_type('setup')
    request.with_status('pending')
    request.with_tier_configuration(tier)

    request = Helper(client).approve_tier_configuration_request(request, 'TL-662-440-096')

    assert request.id() == 'TCR-8027-7606-7082-001'
    asserts.request_status(request.raw(), 'approved')


def test_helper_should_approve_an_already_approved_tier_configuration_request(sync_client_factory, response_factory):
    exception = ClientError(
        message=BAD_REQUEST_400,
        status_code=400,
        error_code="TC_006",
        errors=["Tier configuration request status transition is not allowed."]
    )

    client = sync_client_factory([
        response_factory(exception=exception, status=exception.status_code)
    ])

    tier = TierConfigurationBuilder()
    tier.with_tier_configuration_id('TC-8027-7606-7082')
    tier.with_tier_configuration_status('active')

    request = RequestBuilder()
    request.with_id('TCR-8027-7606-7082-001')
    request.with_type('setup')
    request.with_status('approved')
    request.with_tier_configuration(tier)

    request = Helper(client).approve_tier_configuration_request(request, 'TL-662-440-096')

    assert request.id() == 'TCR-8027-7606-7082-001'
    asserts.request_status(request.raw(), 'approved')


def test_helper_should_fail_approving_a_tier_configuration_request(sync_client_factory, response_factory):
    exception = ClientError(
        message=BAD_REQUEST_400,
        status_code=400,
        error_code="TC_012",
        errors=[
            "There is no tier configuration request template with such id."
        ]
    )

    client = sync_client_factory([
        response_factory(exception=exception, status=exception.status_code)
    ])

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_tier_configuration(TierConfigurationBuilder())

    with pytest.raises(ClientError):
        Helper(client).approve_tier_configuration_request(request, 'TL-662-440-096')


def test_helper_should_fail_a_tier_configuration_request(sync_client_factory, response_factory):
    reason = 'I don\'t like you :P'

    tier_on_server = TierConfigurationBuilder()
    tier_on_server.with_tier_configuration_id('TC-8027-7606-7082')
    tier_on_server.with_tier_configuration_status('processing')

    on_server = RequestBuilder()
    on_server.with_id('TCR-8027-7606-7082-001')
    on_server.with_type('setup')
    on_server.with_status('failed')
    on_server.with_tier_configuration(tier_on_server)
    on_server.with_reason(reason)

    client = sync_client_factory([
        response_factory(value=on_server.raw(), status=200)
    ])

    request = RequestBuilder()
    request.with_id('TCR-8027-7606-7082-001')
    request.with_status('pending')
    request.with_tier_configuration(tier_on_server)

    request = Helper(client).fail_tier_configuration_request(request, reason)

    assert request.id() == 'TCR-8027-7606-7082-001'
    asserts.request_status(request.raw(), 'failed')
    asserts.request_reason(request.raw(), reason)


def test_helper_should_fail_an_already_failed_tier_configuration_request(sync_client_factory, response_factory):
    exception = ClientError(
        message=BAD_REQUEST_400,
        status_code=400,
        error_code="TC_006",
        errors=["Tier configuration request status transition is not allowed."]
    )

    client = sync_client_factory([
        response_factory(exception=exception, status=exception.status_code)
    ])

    tier = TierConfigurationBuilder()
    tier.with_tier_configuration_id('TC-8027-7606-7082')
    tier.with_tier_configuration_status('processing')

    request = RequestBuilder()
    request.with_id('TCR-8027-7606-7082-001')
    request.with_type('setup')
    request.with_status('failed')
    request.with_tier_configuration(tier)

    request = Helper(client).fail_tier_configuration_request(request, 'It is my will')

    assert request.id() == 'TCR-8027-7606-7082-001'
    asserts.request_status(request.raw(), 'failed')


def test_helper_should_fail_failing_a_tier_configuration_request(sync_client_factory, response_factory):
    exception = ClientError(
        message=BAD_REQUEST_400,
        status_code=400,
        error_code="VAL_001",
        errors=["reason: This field may not be blank."]
    )

    client = sync_client_factory([
        response_factory(exception=exception, status=exception.status_code)
    ])

    request = RequestBuilder()
    request.with_id('TCR-8027-7606-7082-001')
    request.with_tier_configuration(TierConfigurationBuilder())

    with pytest.raises(ClientError):
        Helper(client).fail_tier_configuration_request(request, "")


def test_helper_should_inquire_a_tier_configuration_request(sync_client_factory, response_factory):
    tier = TierConfigurationBuilder()
    tier.with_tier_configuration_id('AS-8027-7606-7082')
    tier.with_tier_configuration_status('processing')

    on_server = RequestBuilder()
    on_server.with_id('TCR-8027-7606-7082-001')
    on_server.with_type('setup')
    on_server.with_status('inquiring')
    on_server.with_tier_configuration(tier)

    client = sync_client_factory([
        response_factory(value=on_server.raw(), status=200)
    ])

    request = RequestBuilder()
    request.with_id('TCR-8027-7606-7082-001')
    request.with_type('setup')
    request.with_status('pending')
    request.with_tier_configuration(tier)

    request = Helper(client).inquire_tier_configuration_request(request)

    assert request.id() == 'TCR-8027-7606-7082-001'
    asserts.request_status(request.raw(), 'inquiring')


def test_helper_should_inquire_an_already_inquired_tier_configuration_request(sync_client_factory, response_factory):
    exception = ClientError(
        message=BAD_REQUEST_400,
        status_code=400,
        error_code="TC_006",
        errors=["Tier configuration request status transition is not allowed."]
    )

    client = sync_client_factory([
        response_factory(exception=exception, status=exception.status_code)
    ])

    tier = TierConfigurationBuilder()
    tier.with_tier_configuration_id('TC-8027-7606-7082')
    tier.with_tier_configuration_status('processing')

    request = RequestBuilder()
    request.with_id('TCR-8027-7606-7082-001')
    request.with_type('setup')
    request.with_status('inquiring')
    request.with_tier_configuration(tier)

    request = Helper(client).inquire_tier_configuration_request(request)

    assert request.id() == 'TCR-8027-7606-7082-001'
    asserts.request_status(request.raw(), 'inquiring')


def test_helper_should_fail_inquiring_a_tier_configuration_request(sync_client_factory, response_factory):
    exception = ClientError(
        message=BAD_REQUEST_400,
        status_code=400,
        error_code="TC_006",
        errors=["Some weird error..."]
    )

    client = sync_client_factory([
        response_factory(exception=exception, status=exception.status_code)
    ])

    request = RequestBuilder()
    request.with_id('TCR-8027-7606-7082-001')
    request.with_tier_configuration(TierConfigurationBuilder())

    with pytest.raises(ClientError):
        Helper(client).inquire_tier_configuration_request(request)


def test_helper_should_update_a_request_tier_configuration_params(sync_client_factory, response_factory, load_json):
    on_server = RequestBuilder(load_json(os.path.dirname(__file__) + TIER_CONFIG_REQUEST_FILE))

    after_update = RequestBuilder(load_json(os.path.dirname(__file__) + TIER_CONFIG_REQUEST_FILE))
    after_update.with_param('TIER_SIGNATURE', 'the-tier-signature-updated')
    tier = after_update.tier_configuration()
    tier.with_tier_configuration_param('TIER_SIGNATURE', 'the-tier-signature-updated')
    after_update.with_tier_configuration(tier)

    client = sync_client_factory([
        response_factory(value=on_server.raw(), status=200),
        response_factory(value=after_update.raw(), status=200)
    ])

    request = RequestBuilder(load_json(os.path.dirname(__file__) + TIER_CONFIG_REQUEST_FILE))
    request.with_param('TIER_SIGNATURE', 'the-tier-signature-updated')
    print(request.param('TIER_SIGNATURE'))
    request = Helper(client).update_tier_configuration_parameters(request)

    assert request.raw()['params'][0]['id'] == 'TIER_SIGNATURE'
    assert request.raw()['params'][0]['value'] == 'the-tier-signature-updated'
    asserts.tier_configuration_param_value_equal(request.raw(), 'TIER_SIGNATURE', 'the-tier-signature-updated')


def test_helper_should_not_update_request_tier_configuration_params(sync_client_factory, response_factory, load_json):
    request = RequestBuilder(load_json(os.path.dirname(__file__) + TIER_CONFIG_REQUEST_FILE))

    client = sync_client_factory([
        response_factory(value=request.raw(), status=200),
    ])
    request = Helper(client).update_tier_configuration_parameters(request)

    assert request.raw()['params'][0]['id'] == 'TIER_SIGNATURE'
    assert request.raw()['params'][0]['value'] == ''
    asserts.tier_configuration_param_value_equal(request.raw(), 'TIER_SIGNATURE', '')
