from __future__ import annotations

from typing import Any, List, Optional, Union

from connect.toolkit import _param_members, find_by_id, make_tier, with_member
from connect.toolkit.exceptions import MissingItemError, MissingParameterError


class AssetBuilder:
    def __init__(self, asset: Optional[dict] = None):
        if asset is None:
            asset = {}

        if not isinstance(asset, dict):
            raise ValueError('Asset must be a dictionary.')

        self._asset = asset

    def asset(self) -> dict:
        return self._asset

    def asset_id(self) -> Optional[str]:
        return self._asset.get('id')

    def with_asset_id(self, asset_id: str) -> AssetBuilder:
        with_member(self._asset, 'id', asset_id)
        return self

    def asset_status(self) -> Optional[str]:
        return self._asset.get('status')

    def with_asset_status(self, asset_status: str) -> AssetBuilder:
        with_member(self._asset, 'status', asset_status)
        return self

    def asset_product(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[dict]:
        product = self._asset.get('product')
        if product is None:
            return None

        return product if key is None else product.get(key, default)

    def with_asset_product(self, product_id: str, product_status: str = 'published') -> AssetBuilder:
        with_member(self._asset, 'product', {
            'id': product_id,
            'status': product_status,
        })
        return self

    def asset_marketplace(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[dict]:
        marketplace = self._asset.get('marketplace')
        if marketplace is None:
            return None

        return marketplace if key is None else marketplace.get(key, default)

    def with_asset_marketplace(self, marketplace_id: str, marketplace_name: Optional[str] = None) -> AssetBuilder:
        with_member(self._asset, 'marketplace', {
            'id': marketplace_id,
            'name': marketplace_name,
        })
        return self

    def asset_connection(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[dict]:
        connection = self._asset.get('connection')
        if connection is None:
            return None

        return connection if key is None else connection.get(key, default)

    def with_asset_connection(self, connection_id: str, connection_type: str) -> AssetBuilder:
        with_member(self._asset, 'connection', {
            'id': connection_id,
            'type': connection_type,
        })
        return self

    def asset_tier(
            self,
            tier_name: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[str, dict]]:
        tier = self._asset.get('tiers', {}).get(tier_name)
        if tier is None:
            return None

        return tier if key is None else tier.get(key, default)

    def with_asset_tier(self, tier_name: str, tier: Union[str, dict]) -> AssetBuilder:
        if self._asset.get('tiers') is None:
            self._asset.update({'tiers': {}})

        if self._asset.get('tiers', {}).get(tier_name) is None:
            self._asset.get('tiers', {}).update({tier_name: {}})

        if isinstance(tier, str):
            self._asset.get('tiers', {}).get(tier_name, {}).clear()
            tier = make_tier(tier_name) if tier == 'random' else {'id': tier}

        self._asset.get('tiers', {}).get(tier_name).update(tier)
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
        return self._asset.get('params', [])

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

    def with_asset_params(self, params: List[dict]) -> AssetBuilder:
        with_member(self._asset, 'params', params)
        return self

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
            self.with_asset_params([param])

        members = _param_members(param, value, value_error)
        param.update({k: v for k, v in members.items() if v is not None})
        return self

    def asset_items(self) -> List[dict]:
        return self._asset.get('items', [])

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

    def with_asset_items(self, items: List[dict]):
        with_member(self._asset, 'items', items)

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
            self.with_asset_items([item])

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
            raise MissingItemError(f'Missing item {param_id} in item {item_id}')

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
        return self._asset.get('configuration', {}).get('params', [])

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
        if self._asset.get('configuration') is None:
            self._asset.update({'configuration': {}})

        if self._asset.get('configuration', {}).get('params') is None:
            self._asset.get('configuration', {}).update({'params': []})

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
            self._asset.get('configuration', {}).get('params', []).append(param)

        members = _param_members(param, value, value_error)
        param.update({k: v for k, v in members.items() if v is not None})
        return self
