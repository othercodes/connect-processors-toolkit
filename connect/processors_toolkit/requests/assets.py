#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Union

from connect.processors_toolkit import find_by_id, merge
from connect.processors_toolkit.requests.helpers import make_param, make_tier
from connect.processors_toolkit.requests.exceptions import MissingItemError, MissingParameterError


class AssetBuilder:
    def __init__(self, asset: Optional[dict] = None):
        if asset is None:
            asset = {}

        if not isinstance(asset, dict):
            raise ValueError('Asset must be a dictionary.')

        self._asset = asset

    def __repr__(self) -> str:
        return '{class_name}(asset={asset})'.format(
            class_name=self.__class__.__name__,
            asset=self._asset,
        )

    def __str__(self) -> str:
        return str(self._asset)

    def raw(self, deep_copy: bool = False) -> dict:
        return deepcopy(self._asset) if deep_copy else self._asset

    def without(self, key: str) -> AssetBuilder:
        self._asset.pop(key, None)
        return self

    def asset_id(self) -> Optional[str]:
        return self._asset.get('id')

    def with_asset_id(self, asset_id: str) -> AssetBuilder:
        self._asset.update({'id': asset_id})
        return self

    def asset_external_id(self) -> Optional[str]:
        return self._asset.get('external_id')

    def with_asset_external_id(self, asset_external_id: str) -> AssetBuilder:
        self._asset.update({'external_id': asset_external_id})
        return self

    def asset_external_uid(self) -> Optional[str]:
        return self._asset.get('external_uid')

    def with_asset_external_uid(self, asset_external_uid: str) -> AssetBuilder:
        self._asset.update({'external_uid': asset_external_uid})
        return self

    def asset_status(self) -> Optional[str]:
        return self._asset.get('status')

    def with_asset_status(self, asset_status: str) -> AssetBuilder:
        self._asset.update({'status': asset_status})
        return self

    def asset_product(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        product = self._asset.get('product')
        if product is None:
            return None

        return product if key is None else product.get(key, default)

    def with_asset_product(self, product_id: str, product_status: str = 'published') -> AssetBuilder:
        self._asset.update({'product': merge(self._asset.get('product', {}), {
            'id': product_id,
            'status': product_status,
        })})
        return self

    def asset_marketplace(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        marketplace = self._asset.get('marketplace')
        if marketplace is None:
            return None

        return marketplace if key is None else marketplace.get(key, default)

    def with_asset_marketplace(self, marketplace_id: str, marketplace_name: Optional[str] = None) -> AssetBuilder:
        self._asset.update({'marketplace': merge(self._asset.get('marketplace', {}), {
            'id': marketplace_id,
            'name': marketplace_name,
        })})
        return self

    def asset_connection(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        connection = self._asset.get('connection')
        if connection is None:
            return None

        return connection if key is None else connection.get(key, default)

    def with_asset_connection(
            self,
            connection_id: str,
            connection_type: str,
            provider: Optional[dict] = None,
            vendor: Optional[dict] = None,
            hub: Optional[dict] = None,
    ) -> AssetBuilder:
        self._asset.update({'connection': merge(self._asset.get('connection', {}), {
            'id': connection_id,
            'type': connection_type,
        })})
        if provider is not None:
            self.with_asset_connection_provider(
                provider_id=provider.get('id'),
                provider_name=provider.get('name'),
            )
        if vendor is not None:
            self.with_asset_connection_vendor(
                vendor_id=vendor.get('id'),
                vendor_name=vendor.get('name'),
            )
        if hub is not None:
            self.with_asset_connection_hub(
                hub_id=hub.get('id'),
                hub_name=hub.get('name'),
            )
        return self

    def asset_connection_provider(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        provider = self.asset_connection('provider')
        if provider is None:
            return None

        return provider if key is None else provider.get(key, default)

    def with_asset_connection_provider(self, provider_id: str, provider_name: Optional[str] = None) -> AssetBuilder:
        self._asset.update({'connection': merge(self._asset.get('connection', {}), {'provider': {
            'id': provider_id,
            'name': provider_name,
        }})})
        return self

    def asset_connection_vendor(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        vendor = self.asset_connection('vendor')
        if vendor is None:
            return None

        return vendor if key is None else vendor.get(key, default)

    def with_asset_connection_vendor(self, vendor_id: str, vendor_name: Optional[str] = None) -> AssetBuilder:
        self._asset.update({'connection': merge(self._asset.get('connection', {}), {'vendor': {
            'id': vendor_id,
            'name': vendor_name,
        }})})
        return self

    def asset_connection_hub(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        hub = self.asset_connection('hub')
        if hub is None:
            return None

        return hub if key is None else hub.get(key, default)

    def with_asset_connection_hub(self, hub_id: str, hub_name: Optional[str] = None) -> AssetBuilder:
        self._asset.update({'connection': merge(self._asset.get('connection', {}), {'hub': {
            'id': hub_id,
            'name': hub_name,
        }})})
        return self

    def asset_tier(self, tier_name: str, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        tier = self._asset.get('tiers', {}).get(tier_name)
        if tier is None:
            return None

        return tier if key is None else tier.get(key, default)

    def with_asset_tier(self, tier_name: str, tier: Union[str, dict]) -> AssetBuilder:
        if 'tiers' not in self._asset:
            self._asset.update({'tiers': {}})

        if tier_name not in self._asset.get('tiers', {}):
            self._asset.get('tiers', {}).update({tier_name: {}})

        if isinstance(tier, str):
            self._asset.get('tiers', {}).get(tier_name, {}).clear()
            tier = make_tier(tier_name) if tier == 'random' else {'id': tier}

        self._asset.get('tiers', {}).get(tier_name).update(
            merge(self._asset.get('tiers', {}).get(tier_name), tier),
        )
        return self

    def asset_tier_customer(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        return self.asset_tier('customer', key, default)

    def with_asset_tier_customer(self, customer: Union[str, dict]) -> AssetBuilder:
        return self.with_asset_tier('customer', customer)

    def asset_tier_tier1(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        return self.asset_tier('tier1', key, default)

    def with_asset_tier_tier1(self, tier1: Union[str, dict]) -> AssetBuilder:
        return self.with_asset_tier('tier1', tier1)

    def asset_tier_tier2(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        return self.asset_tier('tier2', key, default)

    def with_asset_tier_tier2(self, tier2: Union[str, dict]) -> AssetBuilder:
        return self.with_asset_tier('tier2', tier2)

    def asset_params(self) -> List[Dict[Any, Any]]:
        return self._asset.get('params', [])

    def asset_param(self, param_id: str, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        parameter = find_by_id(self.asset_params(), param_id)
        if parameter is None:
            raise MissingParameterError(f'Missing parameter {param_id}', param_id)

        return parameter if key is None else parameter.get(key, default)

    def with_asset_params(self, params: List[dict]) -> AssetBuilder:
        for param in params:
            self.with_asset_param(**param)
        return self

    def with_asset_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict, list]] = None,
            value_error: Optional[str] = None,
            value_type: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
    ) -> AssetBuilder:
        try:
            param = self.asset_param(param_id)
        except MissingParameterError:
            param = {'id': param_id}
            self._asset.update({'params': self.asset_params() + [param]})

        members = make_param(param_id, value, value_error, value_type, title, description)
        param.update({k: v for k, v in members.items() if v is not None})
        return self

    def asset_items(self) -> List[Dict[Any, Any]]:
        return self._asset.get('items', [])

    def asset_item(self, item_id: str, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        item = find_by_id(self.asset_items(), item_id)
        if item is None:
            raise MissingItemError(f'Missing item {item_id}', item_id)

        return item if key is None else item.get(key, default)

    def with_asset_items(self, items: List[dict]):
        for item in items:
            self.with_asset_item(**item)
        return self

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
            global_id: Optional[str] = None,
            params: Optional[List[dict]] = None,
    ) -> AssetBuilder:
        try:
            item = self.asset_item(item_id)
        except MissingItemError:
            item = {'id': item_id}
            self._asset.update({'items': self.asset_items() + [item]})

        members = {
            'global_id': global_id,
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
        self.with_asset_item_params(item_id, [] if params is None else params)
        return self

    def asset_item_params(self, item_id: str) -> List[Dict[Any, Any]]:
        return self.asset_item(item_id, 'params', [])

    def asset_item_param(
            self,
            item_id: str,
            param_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        param = find_by_id(self.asset_item(item_id, 'params', []), param_id)
        if param is None:
            raise MissingItemError(f'Missing item {param_id} in item {item_id}', item_id)

        return param if key is None else param.get(key, default)

    def with_asset_item_params(self, item_id: str, params: List[dict]) -> AssetBuilder:
        for param in params:
            self.with_asset_item_param(**{'item_id': item_id, **param})
        return self

    def with_asset_item_param(
            self,
            item_id: str,
            param_id: str,
            value: Optional[Union[str, dict, list]] = None,
            value_type: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
            scope: Optional[str] = None,
            phase: Optional[str] = None,
    ) -> AssetBuilder:
        item = self.asset_item(item_id)
        param = find_by_id(item.get('params', []), param_id)
        if param is None:
            param = {'id': param_id}
            item.get('params', []).append(param)

        members = make_param(
            param_id,
            value,
            None,
            value_type,
            title,
            description,
            'item' if scope is None else scope,
            'configuration' if phase is None else phase,
        )
        param.update({k: v for k, v in members.items() if v is not None})
        return self

    def asset_configuration_params(self) -> List[Dict[Any, Any]]:
        return self._asset.get('configuration', {}).get('params', [])

    def asset_configuration_param(
            self,
            param_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        param = find_by_id(self.asset_configuration_params(), param_id)
        if param is None:
            raise MissingParameterError(f'Missing configuration parameter {param_id}', param_id)

        return param if key is None else param.get(key, default)

    def with_asset_configuration_params(self, params: List[dict]) -> AssetBuilder:
        for param in params:
            self.with_asset_configuration_param(**param)
        return self

    def with_asset_configuration_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict, list]] = None,
            value_error: Optional[str] = None,
            value_type: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
    ) -> AssetBuilder:
        if 'configuration' not in self._asset:
            self._asset.update({'configuration': {}})

        if 'params' not in self._asset.get('configuration', {}):
            self._asset.get('configuration', {}).update({'params': []})

        try:
            param = self.asset_configuration_param(param_id)
        except MissingParameterError:
            param = {'id': param_id}
            self._asset.get('configuration', {}).get('params', []).append(param)

        members = make_param(param_id, value, value_error, value_type, title, description)
        param.update({k: v for k, v in members.items() if v is not None})
        return self
