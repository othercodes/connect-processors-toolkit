import pytest

from connect.toolkit.tier_configurations import TierConfigurationBuilder


def test_tier_configuration_builder_should_raise_value_error_on_invalid_init_value():
    with pytest.raises(ValueError):
        TierConfigurationBuilder([])


def test_tier_configuration_request_builder_should_return_none_on_not_initialized_members():
    request = (
        TierConfigurationBuilder()
    )

    assert request.tier_configuration_account() is None
    assert request.tier_configuration_marketplace() is None
    assert request.tier_configuration_connection() is None
    assert request.tier_configuration_product() is None


def test_tier_configuration_builder_should_build_successfully_a_valid_tier_config_request():
    request = (
        TierConfigurationBuilder()
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

    assert request.tier_configuration_id() == 'TC-000-000-000'
    assert request.tier_configuration_status() == 'active'

    assert request.tier_configuration_marketplace('id') == 'MP-12345'

    assert request.tier_configuration_connection('id') == 'CT-0000-0000-0000'
    assert request.tier_configuration_connection('type') == 'test'

    assert request.tier_configuration_configuration_param_by_id('P_CFG_CFG_ID', 'id') == 'P_CFG_CFG_ID'
    assert request.tier_configuration_configuration_param_by_id('P_CFG_CFG_ID', 'value') == 'CFG_VALUE_UPDATED'

    assert request.tier_configuration_product('id') == 'PRD-000-000-100'
    assert request.tier_configuration_product('status') == 'disabled'

    assert request.tier_configuration_account('id') == 'TA-0000-0000-1000'

    assert request.tier_configuration_tier_level() == 2

    assert request.tier_configuration_param_by_id('PARAM_ID_001', 'id') == 'PARAM_ID_001'
    assert request.tier_configuration_param_by_id('PARAM_ID_001', 'value') == 'VALUE_001_UPDATED'

    assert request.tier_configuration_param_by_id('PARAM_ID_002', 'id') == 'PARAM_ID_002'
    assert request.tier_configuration_param_by_id('PARAM_ID_002', 'value') == 'VALUE_002'

    assert request.tier_configuration_param_by_id('PARAM_ID_003', 'id') == 'PARAM_ID_003'
    assert request.tier_configuration_param_by_id('PARAM_ID_003', 'value') == ''
    assert request.tier_configuration_param_by_id('PARAM_ID_003', 'value_error') == 'Some value error on configuration'
