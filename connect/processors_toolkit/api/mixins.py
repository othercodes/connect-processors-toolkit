#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from typing import Dict, List, Optional, Union, Callable, Any

from connect.client import AsyncConnectClient, ClientError, ConnectClient

from connect.processors_toolkit.requests import RequestBuilder
from connect.processors_toolkit.requests.assets import AssetBuilder

ASSET = 'asset'
APPROVE = 'approve'
INQUIRE = 'inquire'
FAIL = 'fail'
APPROVED = 'approved'
INQUIRING = 'inquiring'
FAILED = 'failed'
TEMPLATE_ID = 'template_id'
ACTIVATION_TILE = 'activation_tile'
EFFECTIVE_DATE = 'effective_date'
REASON = 'reason'
PARAMS = 'params'


def _prepare_parameters(updated_params: List[dict]) -> List[dict]:
    def _key(param: dict) -> str:
        return 'value' if param.get('structured_value') is None else 'structured_value'

    def _map(param: dict) -> dict:
        return {
            'id': param.get('id'),
            _key(param): param.get(_key(param), None),
            'value_error': param.get('value_error', ''),
        }

    return list(map(_map, updated_params))


def _get_new_params(resource_params: List[dict], request_params: List[dict]) -> List[dict]:
    resource_params_ids = [param.get('id') for param in resource_params]
    normalized_request_params = _prepare_parameters(request_params)
    return list(filter(lambda x: x.get('id') not in resource_params_ids, normalized_request_params))


class WithAssetHelper:
    client: Union[ConnectClient, AsyncConnectClient]

    def find_asset(self, asset_id: str) -> AssetBuilder:
        return AssetBuilder(self.client.assets[asset_id].get())

    def find_asset_request(self, request_id: str) -> RequestBuilder:
        return RequestBuilder(self.client.requests[request_id].get())

    def approve_asset_request(
            self,
            request: RequestBuilder,
            template_id: str,
            activation_tile: Optional[str] = None,
            effective_date: Optional[str] = None,
            on_error: Optional[Callable[[ClientError], Any]] = None,
            on_success: Optional[Callable[[RequestBuilder], Any]] = None,
    ) -> RequestBuilder:
        """
        Approves the given request using the given template id.

        :param request: The RequestBuilder object.
        :param template_id: The template id to be used to approve.
        :param activation_tile: The activation tile.
        :param effective_date: The effective date.
        :param on_error: Callback to execute when we got an error.
        :param on_success: Callback to execute when action finished successfully.
        :return: The approved RequestBuilder.
        """
        payload = {
            TEMPLATE_ID: template_id,
            ACTIVATION_TILE: activation_tile,
            EFFECTIVE_DATE: effective_date,
        }

        return self._update_asset_request_status(
            request,
            APPROVE,
            payload,
            on_error,
            on_success,
        )

    def fail_asset_request(
            self,
            request: RequestBuilder,
            reason: str,
            on_error: Optional[Callable[[ClientError], Any]] = None,
            on_success: Optional[Callable[[RequestBuilder], Any]] = None,
    ) -> RequestBuilder:
        """
        Fail the given request using the given reason.

        :param request: The RequestBuilder object.
        :param reason: The reason to fail the request.
        :param on_error: Callback to execute when we got an error.
        :param on_success: Callback to execute when action finished successfully.
        :return: The failed RequestBuilder.
        """
        payload = {REASON: reason}

        request.with_reason(reason)

        return self._update_asset_request_status(
            request,
            FAIL,
            payload,
            on_error,
            on_success,
        )

    def inquire_asset_request(
            self,
            request:
            RequestBuilder,
            template_id: str,
            on_error: Optional[Callable[[ClientError], Any]] = None,
            on_success: Optional[Callable[[RequestBuilder], Any]] = None,
    ) -> RequestBuilder:
        """
        Inquire the given RequestBuilder

        :param request: The RequestBuilder object.
        :param template_id: The template id to be used to inquire.
        :param on_error: Callback to execute when we got an error.
        :param on_success: Callback to execute when action finished successfully.
        :return: The inquired RequestBuilder.
        """
        payload = {
            TEMPLATE_ID: template_id
        }

        return self._update_asset_request_status(
            request,
            INQUIRE,
            payload,
            on_error,
            on_success,
        )

    def update_asset_parameters_request(self, request: RequestBuilder) -> RequestBuilder:
        """
        Update parameters that have been changed from the given RequestBuilder.

        :param request: The RequestBuilder object.
        :return: The updated RequestBuilder.
        """
        current = self.find_asset_request(request.id())
        params = zip(
            _prepare_parameters(current.asset().asset_params()),
            _prepare_parameters(request.asset().asset_params()),
        )

        difference = [new for cur, new in params if cur != new]
        difference.extend(_get_new_params(current.params(), request.params()))

        if len(difference) > 0:
            request = RequestBuilder(self.client.requests[request.id()].update(
                payload={ASSET: {PARAMS: difference}},
            ))

        return request

    def _update_asset_request_status(
            self,
            request: RequestBuilder,
            status: str,
            payload: Dict[str, Any] = None,
            on_error: Optional[Callable[[ClientError], Any]] = None,
            on_success: Optional[Callable[[RequestBuilder], Any]] = None,
    ) -> Any:
        """
        Update Asset Request Status

        :param request: The RequestBuilder object.
        :param status: The template id to be used to inquire.
        :param on_error: Callback to execute when we got an error.
        :param on_success: Callback to execute when action finished successfully.
        :return: The inquired RequestBuilder.
        """
        if on_success is None:
            def on_success(req: RequestBuilder):
                return req

        if on_error is None:
            def on_error(error: ClientError):
                raise error

        statuses = {
            APPROVE: APPROVED,
            INQUIRE: INQUIRING,
            FAIL: FAILED,
        }

        try:
            self.client.requests[request.id()](status).post(payload=payload)

            return on_success(request.with_status(statuses.get(status)))
        except ClientError as e:
            return on_error(e)
