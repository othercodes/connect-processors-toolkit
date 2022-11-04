#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Union

from connect.processors_toolkit.requests.assets import AssetBuilder
from connect.processors_toolkit.requests.helpers import find_by_id, make_param, merge, request_model
from connect.processors_toolkit.requests.tier_configurations import TierConfigurationBuilder
from connect.processors_toolkit.requests.exceptions import MissingParameterError


class RequestBuilder:
    def __init__(self, request: Optional[dict] = None):
        request = {} if request is None else request

        if not isinstance(request, dict):
            raise ValueError('Request must be a dictionary.')

        self._request = request

    def __repr__(self) -> str:
        return '{class_name}(request={request})'.format(
            class_name=self.__class__.__name__,
            request=self._request,
        )

    def __str__(self) -> str:
        return str(self._request)

    def raw(self, deep_copy: bool = False) -> dict:
        return deepcopy(self._request) if deep_copy else self._request

    def request_type(self) -> str:
        return request_model(self.raw())

    def is_tier_config_request(self) -> bool:
        return 'tier-config' == self.request_type()

    def is_asset_request(self) -> bool:
        return 'asset' == self.request_type()

    def without(self, key: str) -> RequestBuilder:
        self._request.pop(key, None)
        return self

    def id(self) -> Optional[str]:
        return self._request.get('id')

    def with_id(self, request_id: str) -> RequestBuilder:
        self._request.update({'id': request_id})
        return self

    def type(self) -> Optional[str]:
        return self._request.get('type')

    def with_type(self, request_type: str) -> RequestBuilder:
        self._request.update({'type': request_type})
        return self

    def status(self) -> Optional[str]:
        return self._request.get('status')

    def with_status(self, request_status) -> RequestBuilder:
        self._request.update({'status': request_status})
        return self

    def marketplace(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        marketplace = self._request.get('marketplace')
        if marketplace is None:
            return None

        return marketplace if key is None else marketplace.get(key, default)

    def with_marketplace(self, marketplace_id: str, marketplace_name: Optional[str] = None) -> RequestBuilder:
        self._request.update({'marketplace': merge(self._request.get('marketplace', {}), {
            'id': marketplace_id,
            'name': marketplace_name,
        })})
        return self

    def note(self) -> Optional[str]:
        return self._request.get('note')

    def with_note(self, note: str) -> RequestBuilder:
        self._request.update({'note': note})
        return self

    def reason(self) -> Optional[str]:
        return self._request.get('reason')

    def with_reason(self, reason: str) -> RequestBuilder:
        self._request.update({'reason': reason})
        return self

    def assignee(self, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        assignee = self._request.get('assignee')
        if assignee is None:
            return None

        return assignee if key is None else assignee.get(key, default)

    def with_assignee(self, assignee_id: str, assignee_name: str, assignee_email: str) -> RequestBuilder:
        self._request.update({'assignee': merge(self._request.get('assignee', {}), {
            'id': assignee_id,
            'name': assignee_name,
            'email': assignee_email,
        })})
        return self

    def params(self) -> List[Dict[Any, Any]]:
        return self._request.get('params', [])

    def param(self, param_id: str, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        parameter = find_by_id(self.params(), param_id)
        if parameter is None:
            raise MissingParameterError(f'Missing parameter {param_id}', param_id)

        return parameter if key is None else parameter.get(key, default)

    def with_params(self, params: List[dict]) -> RequestBuilder:
        for param in params:
            self.with_param(**param)
        return self

    def with_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict, list]] = None,
            value_error: Optional[str] = None,
            value_type: str = 'text',
    ) -> RequestBuilder:
        try:
            param = self.param(param_id)
        except MissingParameterError:
            param = {'id': param_id}
            self._request.update({'params': self.params() + [param]})

        members = make_param(param_id, value, value_error, value_type)
        param.update({k: v for k, v in members.items() if v is not None})
        return self

    def asset(self) -> AssetBuilder:
        return AssetBuilder(self._request.get('asset', {}))

    def with_asset(self, asset: Union[dict, AssetBuilder]) -> RequestBuilder:
        asset = asset if isinstance(asset, dict) else asset.raw()
        self._request.update({'asset': asset})
        return self

    def tier_configuration(self) -> TierConfigurationBuilder:
        return TierConfigurationBuilder(self._request.get('configuration', {}))

    def with_tier_configuration(self, configuration: Union[dict, TierConfigurationBuilder]) -> RequestBuilder:
        configuration = configuration if isinstance(configuration, dict) else configuration.raw()
        self._request.update({'configuration': configuration})
        return self
