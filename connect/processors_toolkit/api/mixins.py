#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Union

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
TIER = 'tier'
ACTIVATION_TILE = 'activation_tile'
EFFECTIVE_DATE = 'effective_date'
REASON = 'reason'
PARAMS = 'params'


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
    ) -> Any:
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
    ) -> Any:
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
            request: RequestBuilder,
            template_id: str,
            on_error: Optional[Callable[[ClientError], Any]] = None,
            on_success: Optional[Callable[[RequestBuilder], Any]] = None,
    ) -> Any:
        """
        Inquire the given RequestBuilder

        :param request: The RequestBuilder object.
        :param template_id: The template id to be used to inquire.
        :param on_error: Callback to execute when we got an error.
        :param on_success: Callback to execute when action finished successfully.
        :return: The inquired RequestBuilder.
        """
        payload = {
            TEMPLATE_ID: template_id,
        }

        return self._update_asset_request_status(
            request,
            INQUIRE,
            payload,
            on_error,
            on_success,
        )

    def update_asset_request_parameters(
            self,
            request: RequestBuilder,
            parameters: List[Dict[str, Any]],
            on_error: Optional[Callable[[ClientError], Any]] = None,
            on_success: Optional[Callable[[RequestBuilder], Any]] = None,
    ) -> Any:
        """
        Update Asset parameters

        :param request: The RequestBuilder object.
        :param parameters: The parameters to update in for the Asset.
        :param on_error: Callback to execute when we got an error.
        :param on_success: Callback to execute when action finished successfully.
        :return: The request
        """
        if on_success is None:
            def on_success(request_: RequestBuilder) -> RequestBuilder:
                return request_

        if on_error is None:
            def on_error(error: ClientError):
                raise error
        try:
            updated = RequestBuilder(self.client.requests[request.id()].update(payload={
                "asset": {
                    "params": parameters,
                },
            }))

            return on_success(
                request.with_asset(updated.asset()),
            )
        except ClientError as e:
            return on_error(e)

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
        :return: RequestBuilder

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
