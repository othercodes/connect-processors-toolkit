from __future__ import annotations

from typing import Any, List, Optional, Union

from connect.toolkit import _param_members, find_by_id, with_member, without_member
from connect.toolkit.assets import AssetBuilder
from connect.toolkit.exceptions import MissingParameterError
from connect.toolkit.tier_configurations import TierConfigurationBuilder


class RequestBuilder:
    def __init__(self, request: Optional[dict] = None):
        request = {} if request is None else request

        if not isinstance(request, dict):
            raise ValueError('Request must be a dictionary.')

        self._request = request

    def request(self) -> dict:
        return self._request

    def without(self, key: str) -> RequestBuilder:
        without_member(self._request, key)
        return self

    def id(self) -> Optional[str]:
        return self._request.get('id')

    def with_id(self, request_id: str) -> RequestBuilder:
        with_member(self._request, 'id', request_id)
        return self

    def type(self) -> Optional[str]:
        return self._request.get('type')

    def with_type(self, request_type: str) -> RequestBuilder:
        with_member(self._request, 'type', request_type)
        return self

    def status(self) -> Optional[str]:
        return self._request.get('status')

    def with_status(self, request_status) -> RequestBuilder:
        with_member(self._request, 'status', request_status)
        return self

    def marketplace(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str]]:
        marketplace = self._request.get('marketplace')
        if marketplace is None:
            return None

        return marketplace if key is None else marketplace.get(key, default)

    def with_marketplace(self, marketplace_id: str, marketplace_name: Optional[str] = None) -> RequestBuilder:
        with_member(self._request, 'marketplace', {
            'id': marketplace_id,
            'name': marketplace_name,
        })
        return self

    def note(self) -> Optional[str]:
        return self._request.get('note')

    def with_note(self, note: str) -> RequestBuilder:
        with_member(self._request, 'note', note)
        return self

    def reason(self) -> Optional[str]:
        return self._request.get('reason')

    def with_reason(self, reason: str) -> RequestBuilder:
        with_member(self._request, 'reason', reason)
        return self

    def assignee(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str]]:
        assignee = self._request.get('assignee')
        if assignee is None:
            return None

        return assignee if key is None else assignee.get(key, default)

    def with_assignee(self, assignee_id: str, assignee_name: str, assignee_email: str) -> RequestBuilder:
        with_member(self.request(), 'assignee', {
            'id': assignee_id,
            'name': assignee_name,
            'email': assignee_email,
        })
        return self

    def params(self) -> List[dict]:
        return self._request.get('params', [])

    def param_by_id(
            self,
            param_id: str,
            key: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> Optional[Union[dict, str]]:
        parameter = find_by_id(self.params(), param_id)
        if parameter is None:
            raise MissingParameterError(f'Missing parameter {param_id}')

        return parameter if key is None else parameter.get(key, default)

    def with_params(self, params: List[dict]) -> RequestBuilder:
        with_member(self._request, 'params', params)
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

            self.with_params([param])

        members = _param_members(param, value, value_error)
        param.update({k: v for k, v in members.items() if v is not None})
        return self


class AssetRequestBuilder(RequestBuilder, AssetBuilder):
    def __init__(self, request: Optional[dict] = None):
        request = {} if request is None else request

        if request.get('asset') is None:
            request.update({'asset': {}})

        RequestBuilder.__init__(self, request)
        AssetBuilder.__init__(self, request.get('asset'))


class TierConfigurationRequestBuilder(RequestBuilder, TierConfigurationBuilder):
    def __init__(self, request: Optional[dict] = None):
        request = {} if request is None else request

        if request.get('configuration') is None:
            request.update({'configuration': {}})

        RequestBuilder.__init__(self, request)
        TierConfigurationBuilder.__init__(self, request.get('configuration'))
