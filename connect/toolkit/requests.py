from __future__ import annotations

from typing import Any, List, Optional, TypeVar, Union

from connect.toolkit import find_by_id, merge


class MissingParameterError(Exception):
    pass


class MissingItemError(Exception):
    pass


S = TypeVar('S', bound='RequestParser')


def _param_members(
        param: dict,
        value: Optional[Union[str, dict]] = None,
        value_error: Optional[str] = None,
) -> dict:
    if isinstance(value, dict):
        key = 'structured_value'
        new_value = param.get(key, {})
        new_value.update(value)
    else:
        key = 'value'
        new_value = value

    return {key: new_value, 'value_error': value_error}


def _make_tier(tier_type: str = 'customer') -> dict:
    return {
        "name": 'Acme LLC',
        "type": tier_type,
        "external_id": "100000",
        "external_uid": "00000000-0000-0000-0000-000000000000",
        "contact_info": {
            "address_line1": "222 Fake Street",
            "address_line2": "1B",
            "city": "City",
            "state": "State",
            "postal_code": "000000",
            "country": "US",
            "contact": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@fake.email.com",
                "phone_number": {
                    "country_code": "+1",
                    "area_code": "100",
                    "phone_number": "123456",
                    "extension": "001",
                },
            },
        },
    }


class RequestBuilder:
    def __init__(self: S, request: Optional[dict] = None):
        if request is None:
            request = {}

        if not isinstance(request, dict):
            raise ValueError('Request must be a dictionary.')

        self._original = request
        self._request = request

    def request(self) -> dict:
        return self._request

    def id(self: S) -> Optional[str]:
        return self._request.get('id')

    def with_id(self: S, request_id: str) -> S:
        self._request = merge(self._request, {'id': request_id})
        return self

    def type(self: S) -> Optional[str]:
        return self._request.get('type')

    def with_type(self: S, request_type: str) -> S:
        self._request = merge(self._request, {'type': request_type})
        return self

    def status(self: S) -> Optional[str]:
        return self._request.get('status')

    def with_status(self: S, request_status) -> S:
        self._request = merge(self._request, {'status': request_status})
        return self

    def note(self: S) -> Optional[str]:
        return self._request.get('note')

    def with_note(self: S, note: str) -> S:
        self._request = merge(self._request, {'note': note})
        return self

    def reason(self: S) -> Optional[str]:
        return self._request.get('reason')

    def with_reason(self: S, reason: str) -> S:
        self._request = merge(self._request, {'reason': reason})
        return self

    def assignee(
            self: S,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str]]:
        assignee = self._request.get('assignee')
        if assignee is None:
            return None

        return assignee if key is None else assignee.get(key, default)

    def with_assignee(self: S, assignee_id: str, assignee_name: str, assignee_email: str) -> S:
        self._request = merge(self._request, {'assignee': {
            'id': assignee_id,
            'name': assignee_name,
            'email': assignee_email,
        }})
        return self


class AssetBuilder(RequestBuilder):
    def asset(self) -> dict:
        return self._request.get('asset', {})

    def asset_id(self) -> Optional[str]:
        return self._request.get('asset', {}).get('id')

    def with_asset_id(self, asset_id: str) -> AssetBuilder:
        self._request = merge(self._request, {'asset': {'id': asset_id}})
        return self

    def asset_status(self) -> Optional[str]:
        return self._request.get('asset', {}).get('status')

    def with_asset_status(self, asset_status: str) -> AssetBuilder:
        self._request = merge(self._request, {'asset': {'status': asset_status}})
        return self

    def asset_product(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[dict]:
        product = self._request.get('asset', {}).get('product')
        if product is None:
            return None

        return product if key is None else product.get(key, default)

    def with_asset_product(self, product_id: str, status: str = 'published') -> AssetBuilder:
        self._request = merge(self._request, {'asset': {'product': {'id': product_id, 'status': status}}})
        return self

    def asset_marketplace(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[dict]:
        marketplace = self._request.get('asset', {}).get('marketplace')
        if marketplace is None:
            return None

        return marketplace if key is None else marketplace.get(key, default)

    def with_asset_marketplace(self, marketplace_id: str) -> AssetBuilder:
        self._request = merge(self._request, {'asset': {'marketplace': {'id': marketplace_id}}})
        return self

    def asset_connection(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[dict]:
        connection = self._request.get('asset', {}).get('connection')
        if connection is None:
            return None

        return connection if key is None else connection.get(key, default)

    def with_asset_connection(self, connection_id: str, connection_type: str) -> AssetBuilder:
        self._request = merge(self._request, {'asset': {'connection': {
            'id': connection_id,
            'type': connection_type,
        }}})
        return self

    def asset_tier(
            self,
            tier_name: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[str, dict]]:
        tier = self._request.get('asset', {}).get('tiers', {}).get(tier_name)
        if tier is None:
            return None

        return tier if key is None else tier.get(key, default)

    def with_asset_tier(self, tier_name: str, tier: Union[str, dict]) -> AssetBuilder:
        if isinstance(tier, str):
            self._request.get('asset', {}).get('tiers', {}).get(tier_name, {}).clear()
            tier = _make_tier(tier_name) if tier == 'random' else {'id': tier}

        self._request = merge(self._request, {'asset': {'tiers': {tier_name: tier}}})
        return self

    def asset_tier_customer(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[str, dict]]:
        return self.asset_tier('customer', key, default)

    def with_asset_tier_customer(self, customer: Union[str, dict]) -> AssetBuilder:
        return self.with_asset_tier('customer', customer)

    def asset_tier_tier1(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[str, dict]]:
        return self.asset_tier('tier1', key, default)

    def with_asset_tier_tier1(self, tier1: Union[str, dict]) -> AssetBuilder:
        return self.with_asset_tier('tier1', tier1)

    def asset_tier_tier2(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[str, dict]]:
        return self.asset_tier('tier2', key, default)

    def with_asset_tier_tier2(self, tier2: Union[str, dict]) -> AssetBuilder:
        return self.with_asset_tier('tier2', tier2)

    def asset_params(self) -> List[dict]:
        return self._request.get('asset', {}).get('params', [])

    def asset_param_by_id(
            self,
            param_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str]]:
        parameter = find_by_id(self.asset_params(), param_id)
        if parameter is None:
            raise MissingParameterError(f'Missing parameter {param_id}')

        return parameter if key is None else parameter.get(key, default)

    def with_asset_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict]] = None,
            value_error: Optional[str] = None,
            value_type: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
    ) -> AssetBuilder:
        try:
            param = self.asset_param_by_id(param_id)
        except MissingParameterError:
            param = {
                'id': param_id,
                'name': param_id,
                'title': f'Parameter {param_id} title.' if title is None else title,
                'description': f'Parameter {param_id} description.' if description is None else description,
                'type': 'text' if value_type is None else value_type,
            }
            self._request = merge(self._request, {'asset': {'params': [param]}})

        members = _param_members(param, value, value_error)
        param.update({k: v for k, v in members.items() if v is not None})
        return self

    def asset_items(self) -> List[dict]:
        return self._request.get('asset', {}).get('items', [])

    def asset_item_by_id(
            self,
            item_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str, list]]:
        item = find_by_id(self.asset_items(), item_id)
        if item is None:
            raise MissingItemError(f'Missing item {item_id}')

        return item if key is None else item.get(key, default)

    def with_asset_item(
            self,
            item_id: str,
            item_mpn: str,
            quantity: str = '1',
            old_quantity: Optional[str] = None,
            item_type: Optional[str] = None,
            period: Optional[str] = None,
            unit: Optional[str] = None,
            display_name: Optional[str] = None,
    ) -> AssetBuilder:
        try:
            item = self.asset_item_by_id(item_id)
        except MissingItemError:
            item = {'id': item_id}
            self._request = merge(self._request, {'asset': {'items': [item]}})

        members = {
            'display_name': display_name,
            'mpn': item_mpn,
            'quantity': quantity,
            'old_quantity': old_quantity,
            'params': [],
            'item_type': item_type,
            'period': period,
            'type': unit,
        }

        item.update({k: v for k, v in members.items() if v is not None})
        return self

    def asset_item_params(self, item_id: str) -> List[dict]:
        return self.asset_item_by_id(item_id, 'params', [])

    def asset_item_param_by_id(
            self,
            item_id: str,
            param_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str]]:
        param = find_by_id(self.asset_item_by_id(item_id, 'params', []), param_id)
        if param is None:
            raise MissingParameterError(f'Missing parameter {param_id} in item {item_id}')

        return param if key is None else param.get(key, default)

    def with_asset_item_param(
            self,
            item_id: str,
            param_id: str,
            value: Optional[str] = None,
            value_type: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
            scope: Optional[str] = None,
            phase: Optional[str] = None,
    ) -> AssetBuilder:
        item = self.asset_item_by_id(item_id)
        param = find_by_id(item.get('params', []), param_id)
        if param is None:
            param = {
                'id': param_id,
                'title': f'Parameter {param_id} title.' if title is None else title,
                'description': f'Parameter {param_id} description.' if description is None else description,
                'type': 'text' if value_type is None else value_type,
                'scope': 'item' if scope is None else scope,
                'phase': 'configuration' if phase is None else phase,
            }
            item['params'].append(param)

        members = _param_members(param, value)
        param.update({k: v for k, v in members.items() if v is not None})
        return self

    def asset_configuration_params(self) -> List[dict]:
        return self._request.get('asset', {}).get('configuration', {}).get('params', [])

    def asset_configuration_param_by_id(
            self,
            param_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str]]:
        param = find_by_id(self.asset_configuration_params(), param_id)
        if param is None:
            raise MissingParameterError(f'Missing configuration parameter {param_id}')

        return param if key is None else param.get(key, default)

    def with_asset_configuration_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict]] = None,
            value_error: Optional[str] = None,
            value_type: Optional[str] = None,
            name: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
    ) -> AssetBuilder:
        try:
            param = self.asset_configuration_param_by_id(param_id)
        except MissingParameterError:
            param = {
                'id': param_id,
                'name': param_id if name is None else name,
                'title': f'Parameter {param_id} title.' if title is None else title,
                'description': f'Parameter {param_id} description.' if description is None else description,
                'type': 'text' if value_type is None else value_type,
            }
            self._request = merge(self._request, {'asset': {'configuration': {'params': [param]}}})

        members = _param_members(param, value, value_error)
        param.update({k: v for k, v in members.items() if v is not None})
        return self


class TierConfigBuilder(RequestBuilder):
    def with_tier_configuration_id(self, tier_configuration_id: str) -> TierConfigBuilder:
        self._request = merge(self._request, {'configuration': {'id': tier_configuration_id}})
        return self

    def with_tier_configuration_status(self, tier_configuration_status: str) -> TierConfigBuilder:
        self._request = merge(self._request, {'configuration': {'status': tier_configuration_status}})
        return self

    def with_tier_configuration_product(self, product_id: str, status: str = 'published') -> TierConfigBuilder:
        self._request = merge(self._request, {'configuration': {'product': {'id': product_id, 'status': status}}})
        return self

    def with_tier_configuration_marketplace(self, marketplace_id: str) -> TierConfigBuilder:
        self._request = merge(self._request, {'configuration': {'marketplace': {'id': marketplace_id}}})
        return self

    def with_tier_configuration_connection(self, connection_id: str, connection_type: str) -> TierConfigBuilder:
        self._request = merge(self._request, {'configuration': {'connection': {
            'id': connection_id,
            'type': connection_type,
        }}})
        return self

    def with_tier_configuration_account(self, account: str = 'random') -> TierConfigBuilder:
        if isinstance(account, str):
            self._request.get('configuration', {}).get('account', {}).clear()
            account = _make_tier('reseller') if account == 'random' else {'id': account}

        self._request = merge(self._request, {'configuration': {'account': account}})
        return self

    def with_tier_configuration_tier_level(self, level: int) -> TierConfigBuilder:
        self._request = merge(self._request, {'configuration': {'tier_level': level}})
        return self

    def with_tier_configuration_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict]] = None,
            value_error: Optional[str] = None,
            value_type: str = 'text',
    ) -> TierConfigBuilder:
        locations = [
            (
                lambda request: request.get('configuration', {}).get('params', []),
                lambda parameter: {'configuration': {'params': [parameter]}},
            ),
            (
                lambda request: request.get('params', []),
                lambda parameter: {'params': [parameter]},
            ),
        ]

        for location in locations:
            param = find_by_id(location[0](self._request), param_id)
            if param is None:
                param = {
                    'id': param_id,
                    'name': param_id,
                    'title': f'Configuration parameter {param_id}',
                    'description': f'Configuration parameter description of {param_id}',
                    'type': value_type,
                }
                self._request = merge(self._request, location[1](param))

            members = _param_members(param, value, value_error)
            param.update({k: v for k, v in members.items() if v is not None})

        return self

    def with_tier_configuration_configuration_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict]] = None,
            value_error: Optional[str] = None,
            value_type: str = 'text',
    ) -> TierConfigBuilder:
        param = find_by_id(
            self._request.get('configuration', {}).get('configuration', {}).get('params', []),
            param_id,
        )
        if param is None:
            param = {
                'id': param_id,
                'title': f'Configuration parameter {param_id}',
                'description': f'Configuration parameter description of {param_id}',
                'type': value_type,
            }
            self._request = merge(self._request, {'configuration': {'configuration': {'params': [param]}}})

        members = _param_members(param, value, value_error)
        param.update({k: v for k, v in members.items() if v is not None})

        return self
