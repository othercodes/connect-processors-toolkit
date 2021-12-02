from connect.toolkit.requests import AssetRequestBuilder, TierConfigRequestBuilder, RequestBuilder


def test_request_should_build_successfully_a_valid_requests():
    request = (
        RequestBuilder()
            .with_id('PR-0000-0000-0000-100')
            .with_type('purchase')
            .with_status('approved')
            .with_note('a note')
            .with_reason('a reason')
            .with_assignee('SU-000-000-000', 'John', 'john.snow@fake.mail.com')
    )

    assert request.id() == 'PR-0000-0000-0000-100'
    assert request.type() == 'purchase'
    assert request.status() == 'approved'
    assert request.note() == 'a note'
    assert request.reason() == 'a reason'
    assert request.assignee('id') == 'SU-000-000-000'
    assert request.assignee('name') == 'John'
    assert request.assignee('email') == 'john.snow@fake.mail.com'


def test_asset_request_should_build_successfully_a_valid_asset_request():
    request = (
        AssetRequestBuilder()
            .with_asset_id('AS-0000-0000-1000')
            .with_asset_status('active')
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


def __test_request_builder_should_build_successfully_a_valid_tier_config_request():
    request = (
        TierConfigRequestBuilder()
            .with_tier_configuration_id('TC-000-000-000')
            .with_tier_configuration_status('active')
            .with_tier_configuration_marketplace('MP-12345')
            .with_tier_configuration_connection('CT-0000-0000-0000', 'test')
            .with_tier_configuration_configuration_param('P_CFG_CFG_ID', 'CFG_VALUE')
            .with_tier_configuration_configuration_param('P_CFG_CFG_ID', 'CFG_VALUE_UPDATED')
            .with_tier_configuration_product('PRD-000-000-100', 'disabled')
            .with_tier_configuration_account('TA-0000-0000-1000')
            .with_tier_configuration_tier_level(2)
            .with_tier_configuration_param('PARAM_ID_001', 'VALUE_001')
            .with_tier_configuration_param('PARAM_ID_002', 'VALUE_002')
            .with_tier_configuration_param('PARAM_ID_003', '', 'Some value error on configuration')
            .with_tier_configuration_param('PARAM_ID_001', 'VALUE_001_UPDATED')
    )

    assert request['configuration']['id'] == 'TC-000-000-000'
    assert request['configuration']['status'] == 'active'

    assert request['configuration']['marketplace']['id'] == 'MP-12345'

    assert request['configuration']['connection']['id'] == 'CT-0000-0000-0000'
    assert request['configuration']['connection']['type'] == 'test'

    assert request['configuration']['configuration']['params'][0]['id'] == 'P_CFG_CFG_ID'
    assert request['configuration']['configuration']['params'][0]['value'] == 'CFG_VALUE_UPDATED'

    assert request['configuration']['product']['id'] == 'PRD-000-000-100'
    assert request['configuration']['product']['status'] == 'disabled'

    assert request['configuration']['account']['id'] == 'TA-0000-0000-1000'

    assert request['configuration']['tier_level'] == 2

    assert request['configuration']['params'][0]['id'] == 'PARAM_ID_001'
    assert request['configuration']['params'][0]['value'] == 'VALUE_001_UPDATED'

    assert request['configuration']['params'][1]['id'] == 'PARAM_ID_002'
    assert request['configuration']['params'][1]['value'] == 'VALUE_002'

    assert request['configuration']['params'][2]['id'] == 'PARAM_ID_003'
    assert request['configuration']['params'][2]['value'] == ''
    assert request['configuration']['params'][2]['value_error'] == 'Some value error on configuration'

    assert request['params'][0]['id'] == 'PARAM_ID_001'
    assert request['params'][0]['value'] == 'VALUE_001_UPDATED'

    assert request['params'][1]['id'] == 'PARAM_ID_002'
    assert request['params'][1]['value'] == 'VALUE_002'

    assert request['params'][2]['id'] == 'PARAM_ID_003'
    assert request['params'][2]['value'] == ''
    assert request['params'][2]['value_error'] == 'Some value error on configuration'
