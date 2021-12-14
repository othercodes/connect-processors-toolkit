from __future__ import annotations

from typing import Any, List, Optional, Union

from connect.toolkit import _param_members, find_by_id, make_tier, with_member
from connect.toolkit.exceptions import MissingParameterError


class TierConfigurationBuilder:
    def __init__(self, tier_config: Optional[dict] = None):
        if tier_config is None:
            tier_config = {}

        if not isinstance(tier_config, dict):
            raise ValueError('Tier Configuration must be a dictionary.')

        self._tier_config = tier_config

    def tier_configuration_id(self) -> Optional[str]:
        return self._tier_config.get('id')

    def with_tier_configuration_id(self, tier_configuration_id: str) -> TierConfigurationBuilder:
        with_member(self._tier_config, 'id', tier_configuration_id)
        return self

    def tier_configuration_status(self) -> Optional[str]:
        return self._tier_config.get('status')

    def with_tier_configuration_status(self, tier_configuration_status: str) -> TierConfigurationBuilder:
        with_member(self._tier_config, 'status', tier_configuration_status)
        return self

    def tier_configuration_product(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[dict]:
        product = self._tier_config.get('product')
        if product is None:
            return None

        return product if key is None else product.get(key, default)

    def with_tier_configuration_product(
            self,
            product_id: str,
            product_status: str = 'published',
    ) -> TierConfigurationBuilder:
        with_member(self._tier_config, 'product', {
            'id': product_id,
            'status': product_status,
        })
        return self

    def tier_configuration_marketplace(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[dict]:
        marketplace = self._tier_config.get('marketplace')
        if marketplace is None:
            return None

        return marketplace if key is None else marketplace.get(key, default)

    def with_tier_configuration_marketplace(
            self,
            marketplace_id: str,
            marketplace_name: Optional[str] = None,
    ) -> TierConfigurationBuilder:
        with_member(self._tier_config, 'marketplace', {
            'id': marketplace_id,
            'name': marketplace_name,
        })
        return self

    def tier_configuration_connection(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[dict]:
        connection = self._tier_config.get('connection')
        if connection is None:
            return None

        return connection if key is None else connection.get(key, default)

    def with_tier_configuration_connection(self, connection_id: str, connection_type: str) -> TierConfigurationBuilder:
        with_member(self._tier_config, 'connection', {
            'id': connection_id,
            'type': connection_type,
        })
        return self

    def tier_configuration_account(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str]]:
        account = self._tier_config.get('account')
        if account is None:
            return None

        return account if key is None else account.get(key, default)

    def with_tier_configuration_account(self, account: str = 'random') -> TierConfigurationBuilder:
        if isinstance(account, str):
            self._tier_config.get('account', {}).clear()
            account = make_tier('reseller') if account == 'random' else {'id': account}

        with_member(self._tier_config, 'account', account)
        return self

    def tier_configuration_tier_level(self) -> Optional[int]:
        return self._tier_config.get('tier_level')

    def with_tier_configuration_tier_level(self, level: int) -> TierConfigurationBuilder:
        with_member(self._tier_config, 'tier_level', level)
        return self

    def tier_configuration_params(self) -> List[dict]:
        return self._tier_config.get('params', [])

    def tier_configuration_param_by_id(
            self,
            param_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str]]:
        parameter = find_by_id(self.tier_configuration_params(), param_id)
        if parameter is None:
            raise MissingParameterError(f'Missing parameter {param_id}')

        return parameter if key is None else parameter.get(key, default)

    def with_tier_configuration_params(self, params: List[dict]) -> TierConfigurationBuilder:
        with_member(self._tier_config, 'params', params)
        return self

    def with_tier_configuration_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict]] = None,
            value_error: Optional[str] = None,
            value_type: str = 'text',
    ) -> TierConfigurationBuilder:
        try:
            param = self.tier_configuration_param_by_id(param_id)
        except MissingParameterError:
            param = {
                'id': param_id,
                'name': param_id,
                'title': f'Configuration parameter {param_id}',
                'description': f'Configuration parameter description of {param_id}',
                'type': value_type,
            }
            self.with_tier_configuration_params([param])

        members = _param_members(param, value, value_error)
        param.update({k: v for k, v in members.items() if v is not None})
        return self

    def tier_configuration_configuration_params(self) -> List[dict]:
        return self._tier_config.get('configuration', {}).get('params', [])

    def tier_configuration_configuration_param_by_id(
            self,
            param_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str]]:
        parameter = find_by_id(self.tier_configuration_configuration_params(), param_id)
        if parameter is None:
            raise MissingParameterError(f'Missing parameter {param_id}')

        return parameter if key is None else parameter.get(key, default)

    def with_tier_configuration_configuration_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict]] = None,
            value_error: Optional[str] = None,
            value_type: str = 'text',
    ) -> TierConfigurationBuilder:
        if self._tier_config.get('configuration') is None:
            self._tier_config.update({'configuration': {}})

        if self._tier_config.get('configuration', {}).get('params') is None:
            self._tier_config.get('configuration', {}).update({'params': []})

        try:
            param = self.tier_configuration_configuration_param_by_id(param_id)
        except MissingParameterError:
            param = {
                'id': param_id,
                'title': f'Configuration parameter {param_id}',
                'description': f'Configuration parameter description of {param_id}',
                'type': value_type,
            }
            self._tier_config.update({'configuration': {'params': [param]}})

        members = _param_members(param, value, value_error)
        param.update({k: v for k, v in members.items() if v is not None})
        return self
