from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from connect.toolkit import _param_members, find_by_id, merge
from connect.toolkit.assets import AssetBuilder
from connect.toolkit.exceptions import MissingParameterError
from connect.toolkit.tier_configurations import TierConfigurationBuilder


class RequestBuilder:
    def __init__(self, request: Optional[dict] = None):
        request = {} if request is None else request

        if not isinstance(request, dict):
            raise ValueError('Request must be a dictionary.')

        self._request = request

    def raw(self) -> dict:
        return self._request

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

    def param_by_id(self, param_id: str, key: Optional[str] = None, default: Optional[Any] = None) -> Optional[Any]:
        parameter = find_by_id(self.params(), param_id)
        if parameter is None:
            raise MissingParameterError(f'Missing parameter {param_id}')

        return parameter if key is None else parameter.get(key, default)

    def with_params(self, params: List[dict]) -> RequestBuilder:
        for param in params:
            self.with_param(**param)
        return self

    def with_param(
            self,
            param_id: str,
            value: Optional[Union[str, dict]] = None,
            value_error: Optional[str] = None,
            value_type: str = 'text',
    ) -> RequestBuilder:
        try:
            param = self.param_by_id(param_id)
        except MissingParameterError:
            param = {
                'id': param_id,
                'name': param_id,
                'title': f'Request parameter {param_id}',
                'description': f'Request parameter description of {param_id}',
                'type': value_type,
            }

            self._request.update({'params': self.params() + [param]})

        members = _param_members(param, value, value_error)
        param.update({k: v for k, v in members.items() if v is not None})
        return self


class AssetRequestBuilder(RequestBuilder, AssetBuilder):
    def __init__(self, request: Optional[dict] = None):
        request = {} if request is None else request

        if 'asset' not in request:
            request.update({'asset': {}})

        RequestBuilder.__init__(self, request)
        AssetBuilder.__init__(self, request.get('asset'))


class TierConfigurationRequestBuilder(RequestBuilder, TierConfigurationBuilder):
    def __init__(self, request: Optional[dict] = None):
        request = {} if request is None else request

        if 'configuration' not in request:
            request.update({'configuration': {}})

        RequestBuilder.__init__(self, request)
        TierConfigurationBuilder.__init__(self, request.get('configuration'))
