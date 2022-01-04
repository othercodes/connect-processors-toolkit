from connect.processors_toolkit import merge, mask


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


def test_mask_function_should_mask_the_required_values():
    payload = {
        'id': '123456',
        'payload': {
            'key': 'mask-this-value',
            'users': [
                {'id': 1, 'password': '1'},
                {'id': 2, 'password': '22'},
                {'id': 3, 'password': '333'}
            ]
        }
    }

    expected = {
        'id': '123456',
        'payload': {
            'key': '***************',
            'users': [
                {'id': 1, 'password': '*'},
                {'id': 2, 'password': '**'},
                {'id': 3, 'password': '***'}
            ]
        }
    }

    assert mask(payload, ['key', 'password']) == expected
