import pytest

from connect.processors_toolkit.requests import RequestBuilder, request_model

NOTE = 'A note'
REASON = 'A reason'
USER_ID = 'US-123-123-123'
USER_NAME = 'Vincent Vega'
USER_EMAIL = 'vicent.vega@pulp.com'


def _shared_request_assertions(raw: dict, r: RequestBuilder):
    assert raw['note'] == r.note() == NOTE
    assert raw['reason'] == r.reason() == REASON

    assert raw['marketplace']['id'] == r.marketplace('id') == 'MP-12345'

    assert raw['assignee']['id'] == r.assignee('id') == USER_ID
    assert raw['assignee']['name'] == r.assignee('name') == USER_NAME
    assert raw['assignee']['email'] == r.assignee('email') == USER_EMAIL

    assert len(raw['params']) == len(r.params()) == 2
    assert raw['params'][0]['id'] == r.param('P_001', 'id') == 'P_001'
    assert raw['params'][0]['value'] == r.param('P_001', 'value') == 'P_001-Value-UPD'
    assert raw['params'][0]['value_error'] == r.param('P_001', 'value_error') == 'P_001-Error-UPD'
    assert raw['params'][1]['id'] == r.param('P_002', 'id') == 'P_002'
    assert raw['params'][1]['value'] == r.param('P_002', 'value') == 'P_002-Value'


def test_request_model_should_successfully_return_the_request_model():
    asset_request = {'type': 'purchase', 'asset': {}}
    assert 'asset' == request_model(asset_request)

    tier_config_request = {'type': 'setup', 'configuration': {}}
    assert 'tier-config' == request_model(tier_config_request)

    undefined_request = {}
    assert 'undefined' == request_model(undefined_request)


def test_request_builder_should_raise_value_error_on_invalid_init_value():
    with pytest.raises(ValueError):
        RequestBuilder([])


def test_request_builder_should_return_none_on_not_initialized_members():
    r = RequestBuilder()

    assert r.marketplace() is None
    assert r.assignee() is None


def test_request_builder_should_remove_required_member_from_request():
    r = RequestBuilder()
    r.with_id('PR-0000-0000-0000-100')
    r.without('id')

    assert r.id() is None


def test_request_should_build_successfully_a_valid_requests():
    r = RequestBuilder()
    r.with_id('PR-001')
    r.with_type('purchase')
    r.with_status('pending')
    r.with_marketplace('MP-12345')
    # duplicate call to ensure the member is not duplicated.
    r.with_marketplace('MP-12345')
    r.with_note(NOTE)
    r.with_reason(REASON)
    r.with_assignee(USER_ID, USER_NAME, USER_EMAIL)
    # duplicate call to ensure the member is not duplicated.
    r.with_assignee(USER_ID, USER_NAME, USER_EMAIL)
    r.with_param('P_001', 'P_001-Value', 'P_001-Error')
    r.with_param('P_001', 'P_001-Value-UPD', 'P_001-Error-UPD')
    r.with_param('P_002', 'P_002-Value', 'P_002-Error')

    raw = r.raw()

    assert raw['id'] == r.id() == 'PR-001'
    assert raw['type'] == r.type() == 'purchase'
    assert raw['status'] == r.status() == 'pending'
    _shared_request_assertions(raw, r)


def test_request_builder_should_build_successfully_a_valid_asset_request():
    r = RequestBuilder()

    a = r.asset()
    a.with_asset_id('AS-001')

    r.with_asset(a)
    r.with_id('TCR-001')
    r.with_type('setup')
    r.with_status('pending')
    r.with_marketplace('MP-12345')
    r.with_note(NOTE)
    r.with_reason(REASON)
    r.with_assignee(USER_ID, USER_NAME, USER_EMAIL)
    r.with_param('P_001', 'P_001-Value', 'P_001-Error')
    r.with_param('P_001', 'P_001-Value-UPD', 'P_001-Error-UPD')
    r.with_param('P_002', 'P_002-Value', 'P_002-Error')

    raw = r.raw()

    assert not r.is_tier_config_request()
    assert r.is_asset_request()

    assert raw['id'] == r.id() == 'TCR-001'
    assert raw['type'] == r.type() == 'setup'
    assert raw['status'] == r.status() == 'pending'
    _shared_request_assertions(raw, r)

    assert raw['asset']['id'] == a.asset_id() == 'AS-001'


def test_tier_configuration_request_builder_should_build_successfully_a_valid_tier_configuration_request():
    r = RequestBuilder()

    t = r.tier_configuration()
    t.with_tier_configuration_id('TC-001')

    r.with_tier_configuration(t)
    r.with_id('TCR-001')
    r.with_type('setup')
    r.with_status('pending')
    r.with_marketplace('MP-12345')
    r.with_note(NOTE)
    r.with_reason(REASON)
    r.with_assignee(USER_ID, USER_NAME, USER_EMAIL)
    r.with_params([
        {'param_id': 'P_001', 'value': 'P_001-Value', 'value_error': 'P_001-Error'},
        {'param_id': 'P_001', 'value': 'P_001-Value-UPD', 'value_error': 'P_001-Error-UPD'},
        {'param_id': 'P_002', 'value': 'P_002-Value', 'value_error': 'P_002-Error'},
    ])

    raw = r.raw()

    assert r.is_tier_config_request()
    assert not r.is_asset_request()

    assert raw['id'] == r.id() == 'TCR-001'
    assert raw['type'] == r.type() == 'setup'
    assert raw['status'] == r.status() == 'pending'
    _shared_request_assertions(raw, r)

    assert raw['configuration']['id'] == t.tier_configuration_id() == 'TC-001'
