import pytest

from connect.toolkit.requests import RequestBuilder, AssetRequestBuilder, TierConfigurationRequestBuilder

NOTE = 'A note'
REASON = 'A reason'
USER_ID = 'US-123-123-123'
USER_NAME = 'Vincent Vega'
USER_EMAIL = 'vicent.vega@pulp.com'


def _shared_assertions(dictionary: dict, request: RequestBuilder):
    assert dictionary['marketplace']['id'] == request.marketplace('id') == 'MP-12345'
    assert dictionary['note'] == request.note() == NOTE
    assert dictionary['reason'] == request.reason() == REASON
    assert dictionary['assignee']['id'] == request.assignee('id') == USER_ID
    assert dictionary['assignee']['name'] == request.assignee('name') == USER_NAME
    assert dictionary['assignee']['email'] == request.assignee('email') == USER_EMAIL
    assert len(dictionary['params']) == len(request.params()) == 2
    assert dictionary['params'][0]['id'] == request.param_by_id('P_001', 'id') == 'P_001'
    assert dictionary['params'][0]['value'] == request.param_by_id('P_001', 'value') == 'P_001-Value-UPD'
    assert dictionary['params'][0]['value_error'] == request.param_by_id('P_001', 'value_error') == 'P_001-Error-UPD'
    assert dictionary['params'][1]['id'] == request.param_by_id('P_002', 'id') == 'P_002'
    assert dictionary['params'][1]['value'] == request.param_by_id('P_002', 'value') == 'P_002-Value'


def test_request_builder_should_raise_value_error_on_invalid_init_value():
    with pytest.raises(ValueError):
        RequestBuilder([])


def test_request_builder_should_return_none_on_not_initialized_members():
    request = RequestBuilder()

    assert request.marketplace() is None
    assert request.assignee() is None


def test_request_builder_should_remove_required_member_from_request():
    request = RequestBuilder()
    request.with_id('PR-0000-0000-0000-100')
    request.without('id')

    assert request.id() is None


def test_request_should_build_successfully_a_valid_requests():
    request = RequestBuilder()
    request.with_id('PR-001')
    request.with_type('purchase')
    request.with_status('approved')
    request.with_marketplace('MP-12345')
    # duplicate call to ensure the member is not duplicated.
    request.with_marketplace('MP-12345')
    request.with_note(NOTE)
    request.with_reason(REASON)
    request.with_assignee(USER_ID, USER_NAME, USER_EMAIL)
    # duplicate call to ensure the member is not duplicated.
    request.with_assignee(USER_ID, USER_NAME, USER_EMAIL)
    request.with_param('P_001', 'P_001-Value', 'P_001-Error')
    request.with_param('P_001', 'P_001-Value-UPD', 'P_001-Error-UPD')
    request.with_param('P_002', 'P_002-Value', 'P_002-Error')

    dictionary = request.raw()

    assert dictionary['id'] == request.id() == 'PR-001'
    assert dictionary['type'] == request.type() == 'purchase'
    assert dictionary['status'] == request.status() == 'approved'

    _shared_assertions(dictionary, request)


def test_asset_builder_should_build_successfully_a_valid_asset_request():
    request = AssetRequestBuilder()
    request.with_asset_id('AS-001')
    request.with_id('PRD-001')
    request.with_type('purchase')
    request.with_status('pending')
    request.with_marketplace('MP-12345')
    request.with_note(NOTE)
    request.with_reason(REASON)
    request.with_assignee(USER_ID, USER_NAME, USER_EMAIL)
    request.with_params([
        {'param_id': 'P_001', 'value': 'P_001-Value', 'value_error': 'P_001-Error'},
        {'param_id': 'P_001', 'value': 'P_001-Value-UPD', 'value_error': 'P_001-Error-UPD'},
        {'param_id': 'P_002', 'value': 'P_002-Value', 'value_error': 'P_002-Error'},
    ])

    dictionary = request.raw()

    assert dictionary['id'] == request.id() == 'PRD-001'
    assert dictionary['type'] == request.type() == 'purchase'
    assert dictionary['status'] == request.status() == 'pending'
    _shared_assertions(dictionary, request)

    assert dictionary['asset']['id'] == request.asset_id() == 'AS-001'


def test_tier_configuration_builder_should_successfully_a_valid_tier_configuration_request():
    request = TierConfigurationRequestBuilder()
    request.with_tier_configuration_id('TC-001')
    request.with_id('TCR-001')
    request.with_type('setup')
    request.with_status('pending')
    request.with_marketplace('MP-12345')
    request.with_note(NOTE)
    request.with_reason(REASON)
    request.with_assignee(USER_ID, USER_NAME, USER_EMAIL)
    request.with_param('P_001', 'P_001-Value', 'P_001-Error')
    request.with_param('P_001', 'P_001-Value-UPD', 'P_001-Error-UPD')
    request.with_param('P_002', 'P_002-Value', 'P_002-Error')

    dictionary = request.raw()

    assert dictionary['id'] == request.id() == 'TCR-001'
    assert dictionary['type'] == request.type() == 'setup'
    assert dictionary['status'] == request.status() == 'pending'
    _shared_assertions(dictionary, request)

    assert dictionary['configuration']['id'] == request.tier_configuration_id() == 'TC-001'
