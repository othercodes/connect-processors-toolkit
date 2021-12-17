from connect.toolkit import request_model, merge


def test_request_model_should_successfully_return_the_request_model():
    asset_request = {'type': 'purchase', 'asset': {}}
    assert 'asset' == request_model(asset_request)

    tier_config_request = {'type': 'setup', 'configuration': {}}
    assert 'tier-config' == request_model(tier_config_request)

    undefined_request = {}
    assert 'undefined' == request_model(undefined_request)


def test_merge_should_merge_complex_structures():
    base = {
        'id': 1,
        'status': 'pending',
        'asset': {
            'status': 'active',
            'params': [
                {'id': 1}
            ]
        }
    }

    override = {
        'asset': {
            'status': 'suspended',
            'params': [
                {'id': 2}
            ]
        }
    }

    merged = merge(base, override)

    assert merged['id'] == 1
    assert merged['status'] == 'pending'
    assert merged['asset']['status'] == 'suspended'
    assert merged['asset']['params'][0]['id'] == 1
    assert merged['asset']['params'][1]['id'] == 2
