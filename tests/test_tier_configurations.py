import pytest

from connect.processors_toolkit.tier_configurations import TierConfigurationBuilder


def test_tier_configuration_builder_should_raise_value_error_on_invalid_init_value():
    with pytest.raises(ValueError):
        TierConfigurationBuilder([])


def test_tier_configuration_request_builder_should_return_none_on_not_initialized_members():
    t = TierConfigurationBuilder()

    assert t.tier_configuration_account() is None
    assert t.tier_configuration_marketplace() is None
    assert t.tier_configuration_connection() is None
    assert t.tier_configuration_connection_provider() is None
    assert t.tier_configuration_connection_vendor() is None
    assert t.tier_configuration_connection_hub() is None
    assert t.tier_configuration_product() is None


def test_tier_configuration_builder_should_remove_required_member_from_tier_configuration():
    t = TierConfigurationBuilder()
    t.with_tier_configuration_id('TCR-0000-0000-0000-100')
    t.without('id')

    assert t.tier_configuration_id() is None


def test_tier_configuration_builder_should_build_successfully_a_valid_tier_configuration():
    t = TierConfigurationBuilder()
    t.with_tier_configuration_id('TC-000-000-000')
    t.with_tier_configuration_status('active')
    t.with_tier_configuration_marketplace('MP-12345')
    t.with_tier_configuration_connection(
        connection_id='CT-0000-0000-0000',
        connection_type='test',
        provider={"id": "PA-800-926", "name": "Gamma Team Provider"},
        vendor={"id": "VA-610-138", "name": "Gamma Team Vendor"},
        hub={"id": "HB-0000-0000", "name": "None"},
    )
    t.with_tier_configuration_configuration_param('P_CFG_CFG_ID', 'CFG_VALUE')
    t.with_tier_configuration_configuration_param('P_CFG_CFG_ID', 'CFG_VALUE_UPDATED')
    t.with_tier_configuration_product('PRD-000-000-100', 'disabled')
    t.with_tier_configuration_account('random')
    t.with_tier_configuration_account({'contact_info': {'country': 'ES'}})
    t.with_tier_configuration_tier_level(2)
    t.with_tier_configuration_params([
        {'param_id': 'PARAM_ID_001', 'value': 'VALUE_001'},
        {'param_id': 'PARAM_ID_002', 'value': 'VALUE_002'},
        {'param_id': 'PARAM_ID_003', 'value': '', 'value_error': 'Some value error'},
        {'param_id': 'PARAM_ID_001', 'value': 'VALUE_001_UPDATED'},
    ])

    raw = t.raw()

    assert raw['id'] == t.tier_configuration_id() == 'TC-000-000-000'
    assert raw['status'] == t.tier_configuration_status() == 'active'

    assert raw['marketplace']['id'] == t.tier_configuration_marketplace('id') == 'MP-12345'

    assert raw['connection']['id'] == t.tier_configuration_connection('id') == 'CT-0000-0000-0000'
    assert raw['connection']['type'] == t.tier_configuration_connection('type') == 'test'
    assert raw['connection']['provider']['id'] == t.tier_configuration_connection_provider('id') == 'PA-800-926'
    assert raw['connection']['provider']['name'] == t.tier_configuration_connection_provider(
        'name') == 'Gamma Team Provider'
    assert raw['connection']['vendor']['id'] == t.tier_configuration_connection_vendor('id') == 'VA-610-138'
    assert raw['connection']['vendor']['name'] == t.tier_configuration_connection_vendor('name') == 'Gamma Team Vendor'
    assert raw['connection']['hub']['id'] == t.tier_configuration_connection_hub('id') == 'HB-0000-0000'
    assert raw['connection']['hub']['name'] == t.tier_configuration_connection_hub('name') == 'None'

    assert raw['product']['id'] == t.tier_configuration_product('id') == 'PRD-000-000-100'
    assert raw['product']['status'] == t.tier_configuration_product('status') == 'disabled'

    assert t.tier_configuration_account('id') is None
    assert raw['account']['external_id'] == t.tier_configuration_account('external_id')
    assert raw['account']['external_uid'] == t.tier_configuration_account('external_uid')
    assert raw['account']['contact_info']['country'] == t.tier_configuration_account('contact_info', {}).get(
        'country') == 'ES'

    assert raw['tier_level'] == t.tier_configuration_tier_level() == 2

    assert len(t.tier_configuration_configuration_params()) == 1
    assert raw['configuration']['params'][0]['id'] == t.tier_configuration_configuration_param(
        'P_CFG_CFG_ID', 'id') == 'P_CFG_CFG_ID'
    assert raw['configuration']['params'][0]['value'] == t.tier_configuration_configuration_param(
        'P_CFG_CFG_ID', 'value') == 'CFG_VALUE_UPDATED'

    assert len(t.tier_configuration_params()) == 3
    assert raw['params'][0]['id'] == t.tier_configuration_param('PARAM_ID_001', 'id') == 'PARAM_ID_001'
    assert raw['params'][0]['value'] == t.tier_configuration_param('PARAM_ID_001', 'value') == 'VALUE_001_UPDATED'
    assert raw['params'][1]['id'] == t.tier_configuration_param('PARAM_ID_002', 'id') == 'PARAM_ID_002'
    assert raw['params'][1]['value'] == t.tier_configuration_param('PARAM_ID_002', 'value') == 'VALUE_002'
    assert raw['params'][2]['id'] == t.tier_configuration_param('PARAM_ID_003', 'id') == 'PARAM_ID_003'
    assert raw['params'][2]['value'] == t.tier_configuration_param('PARAM_ID_003', 'value') == ''
    assert raw['params'][2]['value_error'] == t.tier_configuration_param(
        'PARAM_ID_003', 'value_error') == 'Some value error'
