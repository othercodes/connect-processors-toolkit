import pytest

from connect.toolkit.assets import AssetBuilder


def test_asset_request_builder_should_raise_value_error_on_invalid_init_value():
    with pytest.raises(ValueError):
        AssetBuilder([])


def test_asset_request_builder_should_return_none_on_not_initialized_members():
    request = (
        AssetBuilder()
            .with_asset_item('ITM_ID_1', 'ITM_MPN_1')
    )

    assert request.asset_product() is None
    assert request.asset_marketplace() is None
    assert request.asset_connection() is None
    assert request.asset_tier('customer') is None
    assert request.asset_tier('tier1') is None
    assert request.asset_tier('tier2') is None


def test_asset_request_should_build_successfully_a_valid_asset_request():
    request = (
        AssetBuilder()
            .with_asset_id('AS-0000-0000-1000')
            .with_asset_status('active')
            .with_asset_external_id('123456789')
            .with_asset_external_uid('19bddc10-f58c-42ac-8cc0-a6bd8705eacc')
            .with_asset_product('PRD-000-000-100', 'disabled')
            .with_asset_marketplace('MP-12345')
            .with_asset_connection('CT-0000-0000-0000', 'test')
            .with_asset_tier_customer('random')
            .with_asset_tier_tier1('random')
            .with_asset_tier_tier2('random')
            .with_asset_param('PARAM_ID_001', 'VALUE_001')
            .with_asset_param('PARAM_ID_002', 'VALUE_002')
            .with_asset_param('PARAM_ID_003', '', 'Some value error on asset')
            .with_asset_param('PARAM_ID_001', 'VALUE_001_UPDATED')
            .with_asset_item('ITEM_ID_001', 'ITEM_MPN_001')
            .with_asset_item('ITEM_ID_001', 'ITEM_MPN_001_UPDATED')
            .with_asset_item_param('ITEM_ID_001', 'SOME_ITEM_PARAM_ID', 'ITEM_ID_001_PARAM_VALUE')
            .with_asset_item_param('ITEM_ID_001', 'SOME_ITEM_PARAM_ID', 'ITEM_ID_001_PARAM_VALUE_UPD')
            .with_asset_configuration_param('AS_CFG_ID_001', 'Cfg value', 'Cfg error value')
            .with_asset_configuration_param('AS_CFG_ID_001', 'Cfg value updated', 'Cfg error value updated')
    )

    assert request.asset_id() == 'AS-0000-0000-1000'
    assert request.asset_status() == 'active'

    assert request.asset_external_id() == '123456789'
    assert request.asset_external_uid() == '19bddc10-f58c-42ac-8cc0-a6bd8705eacc'

    assert request.asset_product('id') == 'PRD-000-000-100'
    assert request.asset_product('status') == 'disabled'

    assert request.asset_marketplace('id') == 'MP-12345'

    assert request.asset_connection('type') == 'test'
    assert request.asset_connection('id') == 'CT-0000-0000-0000'

    assert request.asset_tier_customer('id') is None
    assert request.asset_tier_customer('external_uid') == '00000000-0000-0000-0000-000000000000'
    assert request.asset_tier_tier1('id') is None
    assert request.asset_tier_tier1('external_uid') == '00000000-0000-0000-0000-000000000000'
    assert request.asset_tier_tier2('id') is None
    assert request.asset_tier_tier2('external_uid') == '00000000-0000-0000-0000-000000000000'

    assert request.asset_param_by_id('PARAM_ID_001', 'id') == 'PARAM_ID_001'
    assert request.asset_param_by_id('PARAM_ID_001', 'value') == 'VALUE_001_UPDATED'

    assert request.asset_param_by_id('PARAM_ID_002', 'id') == 'PARAM_ID_002'
    assert request.asset_param_by_id('PARAM_ID_002', 'value') == 'VALUE_002'

    assert request.asset_param_by_id('PARAM_ID_003', 'id') == 'PARAM_ID_003'
    assert request.asset_param_by_id('PARAM_ID_003', 'value') == ''
    assert request.asset_param_by_id('PARAM_ID_003', 'value_error') == 'Some value error on asset'

    assert request.asset_item_by_id('ITEM_ID_001', 'id') == 'ITEM_ID_001'
    assert request.asset_item_by_id('ITEM_ID_001', 'mpn') == 'ITEM_MPN_001_UPDATED'

    assert request.asset_item_param_by_id('ITEM_ID_001', 'SOME_ITEM_PARAM_ID', 'id') == 'SOME_ITEM_PARAM_ID'
    assert request.asset_item_param_by_id('ITEM_ID_001', 'SOME_ITEM_PARAM_ID', 'value') == 'ITEM_ID_001_PARAM_VALUE_UPD'

    assert request.asset_configuration_param_by_id('AS_CFG_ID_001', 'id') == 'AS_CFG_ID_001'
    assert request.asset_configuration_param_by_id('AS_CFG_ID_001', 'value') == 'Cfg value updated'
    assert request.asset_configuration_param_by_id('AS_CFG_ID_001', 'value_error') == 'Cfg error value updated'
