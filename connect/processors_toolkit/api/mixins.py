from __future__ import annotations

from typing import List, Optional

from connect.client import ClientError, ConnectClient
from connect.client.models import ResourceSet
from connect.processors_toolkit.requests import RequestBuilder
from connect.processors_toolkit.requests.assets import AssetBuilder

ASSET = "asset"
APPROVE = 'approve'
INQUIRE = 'inquire'
FAIL = 'fail'
TEMPLATE_ID = "template_id"
REASON = 'reason'
PARAMS = 'params'
# connect is always responding with status 400 and error code REQ_003 on all
# bad requests, due to this I need to use the actual error list to match the
# error description instead of the error_code.
ERROR_INVALID_STATUS_TRANSITION_APPROVE = 'Only pending and inquiring requests can be approved.'
ERROR_INVALID_STATUS_TRANSITION_FAIL = 'Only pending requests can be failed.'
ERROR_INVALID_STATUS_TRANSITION_INQUIRE = 'Only pending requests can be moved to inquiring status.'


class WithProductHelper:
    client: ConnectClient

    def get_templates(
            self,
            product_id: str,
            template_scope: Optional[str] = None,
            template_type: Optional[str] = None,
    ) -> ResourceSet:
        """
        Get the list of templates by product id.

        :param product_id: The product id from where get the templates.
        :param template_scope: The template scope (asset, tier, etc.)
        :param template_type: The template type (inquire, activate, etc.)
        :return:
        """
        filters = {'scope': template_scope, 'type': template_type}
        filters = {k: v for k, v in filters.items() if v is not None}

        resource = self.client.products[product_id].templates
        if len(filters.items()) > 0:
            resource = resource.filter(**filters)

        return resource.all()


class WithAssetHelper:
    client: ConnectClient

    def find_asset(self, asset_id: str) -> AssetBuilder:
        return AssetBuilder(self.client.assets[asset_id].get())

    def find_asset_request(self, request_id: str) -> RequestBuilder:
        return RequestBuilder(self.client.requests[request_id].get())

    def approve_asset_request(self, request: RequestBuilder, template_id: str) -> RequestBuilder:
        """
        Approves the given request using the given template id.

        :param request: The RequestBuilder object.
        :param template_id: The template id to be used to approve.
        :return: The approved RequestBuilder.
        """
        try:
            request = self.client.requests[request.id()](APPROVE).post(
                payload={TEMPLATE_ID: template_id},
            )
            return RequestBuilder(request)
        except ClientError as e:
            # "REQ_003 - Only pending and inquiring requests can be approved."
            if ERROR_INVALID_STATUS_TRANSITION_APPROVE in e.errors:
                return request
            raise

    def fail_asset_request(self, request: RequestBuilder, reason: str) -> RequestBuilder:
        """
        Fail the given request using the given reason.

        :param request: The RequestBuilder object.
        :param reason: The reason to fail the request.
        :return: The failed RequestBuilder.
        """
        try:
            request = self.client.requests[request.id()](FAIL).post(
                payload={REASON: reason},
            )
            return RequestBuilder(request)
        except ClientError as e:
            # "REQ_003 - Only pending requests can be failed."
            if ERROR_INVALID_STATUS_TRANSITION_FAIL in e.errors:
                return request
            raise

    def inquire_asset_request(self, request: RequestBuilder, template_id: str) -> RequestBuilder:
        """
        Inquire the given RequestBuilder

        :param request: The RequestBuilder object.
        :param template_id: The template id to be used to inquire.
        :return: The inquired RequestBuilder.
        """
        try:
            request = self.client.requests[request.id()](INQUIRE).post(
                payload={TEMPLATE_ID: template_id},
            )
            return RequestBuilder(request)
        except ClientError as e:
            # "REQ_003 - Only pending requests can be moved to inquiring status."
            if ERROR_INVALID_STATUS_TRANSITION_INQUIRE in e.errors:
                return request
            raise

    def update_asset_parameters_request(self, request: RequestBuilder) -> RequestBuilder:
        """
        Update parameters that have been changed from the given RequestBuilder.

        :param request: The RequestBuilder object.
        :return: The updated RequestBuilder.
        """

        def _prepare_asset_parameters(asset_params: List[dict]) -> List[dict]:
            def _key(param: dict) -> str:
                return 'value' if param.get('structured_value') is None else 'structured_value'

            def _map(param: dict) -> dict:
                return {
                    'id': param.get('id'),
                    _key(param): param.get(_key(param), None),
                    'value_error': param.get('value_error', ''),
                }

            return list(map(_map, asset_params))

        current = self.find_asset_request(request.id())
        params = zip(
            _prepare_asset_parameters(current.asset().asset_params()),
            _prepare_asset_parameters(request.asset().asset_params()),
        )

        difference = [new for cur, new in params if cur != new]
        if len(difference) > 0:
            request = RequestBuilder(self.client.requests[request.id()].update(
                payload={ASSET: {PARAMS: difference}},
            ))

        return request
