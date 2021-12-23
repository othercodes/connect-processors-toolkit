import pytest

from connect.processors_toolkit.assets import AssetBuilder
from connect.processors_toolkit.exceptions import MissingItemError


def test_asset_builder_should_raise_value_error_on_invalid_init_value():
    with pytest.raises(ValueError):
        AssetBuilder([])


def test_asset_builder_should_return_none_on_not_initialized_members():
    a = AssetBuilder()
    a.with_asset_item('ITM_ID_1', 'ITM_MPN_1')

    assert a.asset_product() is None
    assert a.asset_marketplace() is None
    assert a.asset_connection() is None
    assert a.asset_connection_provider() is None
    assert a.asset_connection_vendor() is None
    assert a.asset_connection_hub() is None
    assert a.asset_tier('customer') is None
    assert a.asset_tier('tier1') is None
    assert a.asset_tier('tier2') is None


def test_asset_builder_should_remove_required_member_from_asset():
    a = AssetBuilder()
    a.with_asset_id('PR-0000-0000-0000-100')
    a.without('id')

    assert a.asset_id() is None


def test_asset_builder_should_raise_exception_on_adding_parameter_to_missing_asset_item():
    with pytest.raises(MissingItemError):
        a = AssetBuilder()
        a.with_asset_item('ITEM_ID_001', 'ITEM_MPN_001')
        a.asset_item_param('ITEM_ID_001', 'PARAM_ID', 'The value')

    with pytest.raises(MissingItemError):
        a = AssetBuilder()
        a.with_asset_item_param('MISSING', 'PARAM_ID', 'The value')


def test_asset_builder_should_build_successfully_a_valid_asset():
    a = AssetBuilder()
    a.with_asset_id('AS-001')
    a.with_asset_status('active')
    a.with_asset_external_id('123456789')
    a.with_asset_external_uid('9fb50525-a4a4-41a7-ace0-dc3c73796d32')
    a.with_asset_product('PRD-000-000-100', 'disabled')
    a.with_asset_tier_customer('random')
    a.with_asset_tier_tier1('random')
    a.with_asset_tier_tier2('random')
    a.with_asset_tier_tier2({'contact_info': {'country': 'ES'}})
    a.with_asset_marketplace('MP-12345')
    a.with_asset_connection(
        connection_id='CT-0000-0000-0000',
        connection_type='test',
        provider={"id": "PA-800-926", "name": "Gamma Team Provider"},
        vendor={"id": "VA-610-138", "name": "Gamma Team Vendor"},
        hub={"id": "HB-0000-0000", "name": "None"},
    )
    a.with_asset_params([
        {'param_id': 'PARAM_ID_001', 'value': 'VALUE_001'},
        {'param_id': 'PARAM_ID_002', 'value': 'VALUE_002'},
        {'param_id': 'PARAM_ID_003', 'value': '', 'value_error': 'Some value error'},
        {'param_id': 'PARAM_ID_001', 'value': 'VALUE_001_UPDATED'},
    ])
    a.with_asset_items([
        {
            'item_id': 'ITEM_ID_001',
            'item_mpn': 'ITEM_MPN_001',
            'params': [{'param_id': 'SOME_ITEM_PARAM_ID', 'value': 'ITEM_ID_001_PARAM_VALUE'}]
        },
        {
            'item_id': 'ITEM_ID_001',
            'item_mpn': 'ITEM_MPN_001_UPDATED',
        },
        {
            'item_id': 'ITEM_ID_001',
            'item_mpn': 'ITEM_MPN_001_UPDATED',
            'params': [{'param_id': 'SOME_ITEM_PARAM_ID', 'value': 'ITEM_ID_001_PARAM_VALUE_UPDATED'}]
        }
    ])
    a.with_asset_configuration_params([
        {'param_id': 'AS_CFG_ID_001', 'value': 'Cfg value', 'value_error': 'Cfg error value'},
        {'param_id': 'AS_CFG_ID_001', 'value': 'Cfg value updated', 'value_error': 'Cfg error value updated'},
    ])

    raw = a.raw()

    assert raw['id'] == a.asset_id() == 'AS-001'
    assert raw['status'] == a.asset_status() == 'active'

    assert raw['external_id'] == a.asset_external_id() == '123456789'
    assert raw['external_uid'] == a.asset_external_uid() == '9fb50525-a4a4-41a7-ace0-dc3c73796d32'

    assert raw['marketplace']['id'] == a.asset_marketplace('id') == 'MP-12345'

    assert a.asset_tier_customer('id') is None
    assert raw['tiers']['customer']['external_id'] == a.asset_tier_customer('external_id')
    assert raw['tiers']['customer']['external_uid'] == a.asset_tier_customer('external_uid')
    assert a.asset_tier_tier1('id') is None
    assert raw['tiers']['tier1']['external_id'] == a.asset_tier_tier1('external_id')
    assert raw['tiers']['tier1']['external_uid'] == a.asset_tier_tier1('external_uid')
    assert a.asset_tier_tier2('id') is None
    assert raw['tiers']['tier2']['external_id'] == a.asset_tier_tier2('external_id')
    assert raw['tiers']['tier2']['external_uid'] == a.asset_tier_tier2('external_uid')
    assert raw['tiers']['tier2']['contact_info']['country'] == a.asset_tier_tier2('contact_info', {}).get('country')
    assert a.asset_tier_tier2('contact_info', {}).get('country') == 'ES'

    assert raw['connection']['id'] == a.asset_connection('id') == 'CT-0000-0000-0000'
    assert raw['connection']['type'] == a.asset_connection('type') == 'test'
    assert raw['connection']['provider']['id'] == a.asset_connection_provider('id') == 'PA-800-926'
    assert raw['connection']['provider']['name'] == a.asset_connection_provider('name') == 'Gamma Team Provider'
    assert raw['connection']['vendor']['id'] == a.asset_connection_vendor('id') == 'VA-610-138'
    assert raw['connection']['vendor']['name'] == a.asset_connection_vendor('name') == 'Gamma Team Vendor'
    assert raw['connection']['hub']['id'] == a.asset_connection_hub('id') == 'HB-0000-0000'
    assert raw['connection']['hub']['name'] == a.asset_connection_hub('name') == 'None'

    assert raw['product']['id'] == a.asset_product('id') == 'PRD-000-000-100'
    assert raw['product']['status'] == a.asset_product('status') == 'disabled'

    assert len(a.asset_params()) == 3
    assert raw['params'][0]['id'] == a.asset_param('PARAM_ID_001', 'id') == 'PARAM_ID_001'
    assert raw['params'][0]['value'] == a.asset_param('PARAM_ID_001', 'value') == 'VALUE_001_UPDATED'

    assert raw['params'][1]['id'] == a.asset_param('PARAM_ID_002', 'id') == 'PARAM_ID_002'
    assert raw['params'][1]['value'] == a.asset_param('PARAM_ID_002', 'value') == 'VALUE_002'

    assert raw['params'][2]['id'] == a.asset_param('PARAM_ID_003', 'id') == 'PARAM_ID_003'
    assert raw['params'][2]['value'] == a.asset_param('PARAM_ID_003', 'value') == ''
    assert raw['params'][2]['value_error'] == a.asset_param('PARAM_ID_003', 'value_error') == 'Some value error'

    assert len(a.asset_items()) == 1
    assert raw['items'][0]['id'] == a.asset_item('ITEM_ID_001', 'id') == 'ITEM_ID_001'
    assert raw['items'][0]['mpn'] == a.asset_item('ITEM_ID_001', 'mpn') == 'ITEM_MPN_001_UPDATED'

    assert len(a.asset_item_params('ITEM_ID_001')) == 1
    assert raw['items'][0]['params'][0]['id'] == a.asset_item_param(
        'ITEM_ID_001', 'SOME_ITEM_PARAM_ID', 'id') == 'SOME_ITEM_PARAM_ID'
    assert raw['items'][0]['params'][0]['value'] == a.asset_item_param(
        'ITEM_ID_001', 'SOME_ITEM_PARAM_ID', 'value') == 'ITEM_ID_001_PARAM_VALUE_UPDATED'

    assert raw['configuration']['params'][0]['id'] == a.asset_configuration_param(
        'AS_CFG_ID_001', 'id') == 'AS_CFG_ID_001'
    assert raw['configuration']['params'][0]['value'] == a.asset_configuration_param(
        'AS_CFG_ID_001', 'value') == 'Cfg value updated'
    assert raw['configuration']['params'][0]['value_error'] == a.asset_configuration_param(
        'AS_CFG_ID_001', 'value_error') == 'Cfg error value updated'
