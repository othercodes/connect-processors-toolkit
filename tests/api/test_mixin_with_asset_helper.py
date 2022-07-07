import pytest

import os

from connect.client import ConnectClient, ClientError
from connect.devops_testing import asserts
from connect.processors_toolkit.requests import RequestBuilder
from connect.processors_toolkit.requests.assets import AssetBuilder
from connect.processors_toolkit.api.mixins import WithAssetHelper


class Helper(WithAssetHelper):
    def __init__(self, client: ConnectClient):
        self.client = client


BAD_REQUEST_400 = "400 Bad Request"
ASSET_REQUEST_FILE = '/request_asset.json'


def test_asset_helper_should_retrieve_an_asset_by_id(sync_client_factory, response_factory):
    asset = AssetBuilder()
    asset.with_asset_id('AS-9091-4850-9712')

    client = sync_client_factory([
        response_factory(value=asset.raw(), status=200)
    ])

    asset = Helper(client).find_asset('AS-9091-4850-9712')

    assert isinstance(asset, AssetBuilder)
    assert asset.asset_id() == 'AS-9091-4850-9712'


def test_asset_helper_should_retrieve_an_asset_request_by_id(sync_client_factory, response_factory):
    asset = AssetBuilder()
    asset.with_asset_id('AS-9091-4850-9712')

    request = RequestBuilder()
    request.with_id('PR-9091-4850-9712-001')
    request.with_type('purchase')
    request.with_status('pending')
    request.with_asset(asset)

    client = sync_client_factory([
        response_factory(value=request.raw(), status=200)
    ])

    request = Helper(client).find_asset_request('PR-9091-4850-9712-001')

    assert isinstance(request, RequestBuilder)
    assert request.id() == 'PR-9091-4850-9712-001'


def test_asset_helper_should_approve_an_asset_request(sync_client_factory, response_factory):
    asset = AssetBuilder()
    asset.with_asset_id('AS-8027-7606-7082')
    asset.with_asset_status('active')

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_type('purchase')
    request.with_status('approved')
    request.with_asset(asset)

    client = sync_client_factory([
        response_factory(value=request.raw(), status=200)
    ])

    asset = request.asset()
    asset.with_asset_status('processing')

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_type('purchase')
    request.with_status('pending')
    request.with_asset(asset)

    request = Helper(client).approve_asset_request(request, 'TL-662-440-096')

    assert request.id() == 'PR-8027-7606-7082-001'
    asserts.request_status(request.raw(), 'approved')


def test_asset_helper_should_fail_approving_an_asset_request(sync_client_factory, response_factory):
    exception = ClientError(
        message=BAD_REQUEST_400,
        status_code=400,
        error_code="VAL_001",
        errors=[
            "effective_date: Datetime has wrong format. Use one of these formats "
            "instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
        ]
    )

    client = sync_client_factory([
        response_factory(exception=exception, status=exception.status_code)
    ])

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_asset(AssetBuilder())

    with pytest.raises(ClientError):
        Helper(client).approve_asset_request(request, 'TL-662-440-096')


def test_asset_helper_should_fail_an_asset_request(sync_client_factory, response_factory):
    reason = 'I don\'t like you :P'

    asset = AssetBuilder()
    asset.with_asset_id('AS-8027-7606-7082')
    asset.with_asset_status('processing')

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_type('purchase')
    request.with_status('failed')
    request.with_asset(asset)
    request.with_reason(reason)

    client = sync_client_factory([
        response_factory(value=request.raw(), status=200)
    ])

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_status('pending')
    request.with_asset(asset)

    request = Helper(client).fail_asset_request(request, reason)

    assert request.id() == 'PR-8027-7606-7082-001'
    asserts.request_status(request.raw(), 'failed')
    asserts.request_reason(request.raw(), reason)



def test_asset_helper_should_fail_failing_an_asset_request(sync_client_factory, response_factory):
    exception = ClientError(
        message=BAD_REQUEST_400,
        status_code=400,
        error_code="REQ_005",
        errors=["Missed fields: reason."]
    )

    client = sync_client_factory([
        response_factory(exception=exception, status=exception.status_code)
    ])

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_asset(AssetBuilder())

    with pytest.raises(ClientError):
        Helper(client).fail_asset_request(request, 'This is not going to work')


def test_asset_helper_should_inquire_an_asset_request(sync_client_factory, response_factory):
    asset = AssetBuilder()
    asset.with_asset_id('AS-8027-7606-7082')
    asset.with_asset_status('processing')

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_type('purchase')
    request.with_status('inquiring')
    request.with_asset(asset)

    client = sync_client_factory([
        response_factory(value=request.raw(), status=200)
    ])

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_type('purchase')
    request.with_status('pending')
    request.with_asset(asset)

    Helper(client).inquire_asset_request(request, 'TL-662-440-097')

    assert request.id() == 'PR-8027-7606-7082-001'
    asserts.request_status(request.raw(), 'inquiring')


def test_asset_helper_should_fail_inquiring_an_asset_request(sync_client_factory, response_factory):
    exception = ClientError(
        message=BAD_REQUEST_400,
        status_code=400,
        error_code="REQ_003",
        errors=["For marking request to inquiring status at least one parameter should be marked as invalid."]
    )

    client = sync_client_factory([
        response_factory(exception=exception, status=exception.status_code)
    ])

    request = RequestBuilder()
    request.with_id('PR-8027-7606-7082-001')
    request.with_asset(AssetBuilder())

    with pytest.raises(ClientError):
        Helper(client).inquire_asset_request(request, 'TL-662-440-097')


def test_asset_helper_should_update_a_request_asset_params(sync_client_factory, response_factory, load_json):
    on_server = RequestBuilder(load_json(os.path.dirname(__file__) + ASSET_REQUEST_FILE))

    after_update = RequestBuilder(load_json(os.path.dirname(__file__) + ASSET_REQUEST_FILE))
    asset = after_update.asset()
    asset.with_asset_param('CAT_SUBSCRIPTION_ID', 'AS-8790-0160-2196')
    after_update.with_asset(asset)

    client = sync_client_factory([
        response_factory(value=on_server.raw(), status=200),
        response_factory(value=after_update.raw(), status=200)
    ])

    request = RequestBuilder(load_json(os.path.dirname(__file__) + ASSET_REQUEST_FILE))
    asset = request.asset()
    asset.with_asset_param('CAT_SUBSCRIPTION_ID', 'AS-8790-0160-2196')
    request.with_asset(asset)

    request = Helper(client).update_asset_parameters_request(request)

    asserts.asset_param_value_equal(request.raw(), 'CAT_SUBSCRIPTION_ID', 'AS-8790-0160-2196')


def test_asset_helper_should_not_update_request_asset_params(sync_client_factory, response_factory, load_json):
    request = RequestBuilder(load_json(os.path.dirname(__file__) + ASSET_REQUEST_FILE))

    client = sync_client_factory([
        response_factory(value=request.raw(), status=200),
    ])
    request = Helper(client).update_asset_parameters_request(request)

    asserts.asset_param_value_equal(request.raw(), 'CAT_SUBSCRIPTION_ID', '')
