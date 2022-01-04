from __future__ import annotations

from typing import Any, List, Optional, Union

from connect.processors_toolkit import find_by_id, make_param, make_tier, merge
from connect.processors_toolkit.exceptions import MissingParameterError


class TierConfigurationBuilder:
    def __init__(self, tier_config: Optional[dict] = None):
        if tier_config is None:
            tier_config = {}

        if not isinstance(tier_config, dict):
            raise ValueError('Tier Configuration must be a dictionary.')

        self._tier_config = tier_config

    def __repr__(self) -> str:
        return '{class_name}(tier_config={tier_config})'.format(
            class_name=self.__class__.__name__,
            tier_config=self._tier_config,
        )

    def __str__(self) -> str:
        return str(self._tier_config)

    def raw(self) -> dict:
        return self._tier_config

    def without(self, key: str) -> TierConfigurationBuilder:
        self._tier_config.pop(key, None)
        return self

    def tier_configuration_id(self) -> Optional[str]:
        return self._tier_config.get('id')

    def with_tier_configuration_id(self, tier_configuration_id: str) -> TierConfigurationBuilder:
        self._tier_config.update({'id': tier_configuration_id})
        return self

    def tier_configuration_status(self) -> Optional[str]:
        return self._tier_config.get('status')

    def with_tier_configuration_status(self, tier_configuration_status: str) -> TierConfigurationBuilder:
        self._tier_config.update({'status': tier_configuration_status})
        return self

    def tier_configuration_product(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        product = self._tier_config.get('product')
        if product is None:
            return None

        return product if key is None else product.get(key, default)

    def with_tier_configuration_product(
            self,
            product_id: str,
            product_status: str = 'published',
    ) -> TierConfigurationBuilder:
        self._tier_config.update({'product': merge(self._tier_config.get('product', {}), {
            'id': product_id,
            'status': product_status,
        })})
        return self

    def tier_configuration_marketplace(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        marketplace = self._tier_config.get('marketplace')
        if marketplace is None:
            return None

        return marketplace if key is None else marketplace.get(key, default)

    def with_tier_configuration_marketplace(
            self,
            marketplace_id: str,
            marketplace_name: Optional[str] = None,
    ) -> TierConfigurationBuilder:
        self._tier_config.update({'marketplace': merge(self._tier_config.get('marketplace', {}), {
            'id': marketplace_id,
            'name': marketplace_name,
        })})
        return self

    def tier_configuration_connection(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        connection = self._tier_config.get('connection')
        if connection is None:
            return None

        return connection if key is None else connection.get(key, default)

    def with_tier_configuration_connection(
            self,
            connection_id: str,
            connection_type: str,
            provider: Optional[dict] = None,
            vendor: Optional[dict] = None,
            hub: Optional[dict] = None,
    ) -> TierConfigurationBuilder:
        self._tier_config.update({'connection': merge(self._tier_config.get('connection', {}), {
            'id': connection_id,
            'type': connection_type,
        })})
        if provider is not None:
            self.with_tier_configuration_connection_provider(
                provider_id=provider.get('id'),
                provider_name=provider.get('name'),
            )
        if vendor is not None:
            self.with_tier_configuration_connection_vendor(
                vendor_id=vendor.get('id'),
                vendor_name=vendor.get('name'),
            )
        if hub is not None:
            self.with_tier_configuration_connection_hub(
                hub_id=hub.get('id'),
                hub_name=hub.get('name'),
            )
        return self

    def tier_configuration_connection_provider(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        provider = self.tier_configuration_connection('provider')
        if provider is None:
            return None

        return provider if key is None else provider.get(key, default)

    def with_tier_configuration_connection_provider(
            self,
            provider_id: str,
            provider_name: Optional[str] = None,
    ) -> TierConfigurationBuilder:
        self._tier_config.update({'connection': merge(self._tier_config.get('connection', {}), {'provider': {
            'id': provider_id,
            'name': provider_name,
        }})})
        return self

    def tier_configuration_connection_vendor(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        vendor = self.tier_configuration_connection('vendor')
        if vendor is None:
            return None

        return vendor if key is None else vendor.get(key, default)

    def with_tier_configuration_connection_vendor(
            self,
            vendor_id: str,
            vendor_name: Optional[str] = None,
    ) -> TierConfigurationBuilder:
        self._tier_config.update({'connection': merge(self._tier_config.get('connection', {}), {'vendor': {
            'id': vendor_id,
            'name': vendor_name,
        }})})
        return self

    def tier_configuration_connection_hub(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        hub = self.tier_configuration_connection('hub')
        if hub is None:
            return None

        return hub if key is None else hub.get(key, default)

    def with_tier_configuration_connection_hub(
            self,
            hub_id: str,
            hub_name: Optional[str] = None,
    ) -> TierConfigurationBuilder:
        self._tier_config.update({'connection': merge(self._tier_config.get('connection', {}), {'hub': {
            'id': hub_id,
            'name': hub_name,
        }})})
        return self

    def tier_configuration_account(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        account = self._tier_config.get('account')
        if account is None:
            return None

        return account if key is None else account.get(key, default)

    def with_tier_configuration_account(
            self,
            account: Optional[Union[str, dict]] = 'random',
    ) -> TierConfigurationBuilder:
        if isinstance(account, str):
            self._tier_config.get('account', {}).clear()
            account = make_tier('reseller') if account == 'random' else {'id': account}

        self._tier_config.update({'account': merge(self._tier_config.get('account', {}), account)})
        return self

    def tier_configuration_tier_level(self) -> Optional[int]:
        return self._tier_config.get('tier_level')

    def with_tier_configuration_tier_level(self, level: int) -> TierConfigurationBuilder:
        self._tier_config.update({'tier_level': level})
        return self

    def tier_configuration_params(self) -> List[dict]:
        return self._tier_config.get('params', [])

    def tier_configuration_param(
            self,
            param_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        parameter = find_by_id(self.tier_configuration_params(), param_id)
        if parameter is None:
            raise MissingParameterError(f'Missing parameter {param_id}', param_id)

        return parameter if key is None else parameter.get(key, default)

    def with_tier_configuration_params(self, params: List[dict]) -> TierConfigurationBuilder:
        for param in params:
            self.with_tier_configuration_param(**param)
        return self

    def with_tier_configuration_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict]] = None,
            value_error: Optional[str] = None,
            value_type: Optional[str] = None,
    ) -> TierConfigurationBuilder:
        try:
            param = self.tier_configuration_param(param_id)
        except MissingParameterError:
            param = {'id': param_id}
            self._tier_config.update({'params': self.tier_configuration_params() + [param]})

        members = make_param(param_id, value, value_error, value_type)
        param.update({k: v for k, v in members.items() if v is not None})
        return self

    def tier_configuration_configuration_params(self) -> List[dict]:
        return self._tier_config.get('configuration', {}).get('params', [])

    def tier_configuration_configuration_param(
            self,
            param_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Any]:
        parameter = find_by_id(self.tier_configuration_configuration_params(), param_id)
        if parameter is None:
            raise MissingParameterError(f'Missing parameter {param_id}', param_id)

        return parameter if key is None else parameter.get(key, default)

    def with_tier_configuration_configuration_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict]] = None,
            value_error: Optional[str] = None,
            value_type: Optional[str] = None,
    ) -> TierConfigurationBuilder:
        if 'configuration' not in self._tier_config:
            self._tier_config.update({'configuration': {}})

        if 'params' not in self._tier_config.get('configuration', {}):
            self._tier_config.get('configuration', {}).update({'params': []})

        try:
            param = self.tier_configuration_configuration_param(param_id)
        except MissingParameterError:
            param = {'id': param_id}
            self._tier_config.get('configuration', {}).get('params', []).append(param)

        members = make_param(param_id, value, value_error, value_type)
        param.update({k: v for k, v in members.items() if v is not None})
        return self
