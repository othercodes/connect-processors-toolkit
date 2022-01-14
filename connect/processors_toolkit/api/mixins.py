from __future__ import annotations

from typing import List, Optional, Union

from connect.client import AsyncConnectClient, ClientError, ConnectClient
from connect.processors_toolkit.requests import RequestBuilder
from connect.processors_toolkit.requests.assets import AssetBuilder
from connect.processors_toolkit.requests.tier_configurations import TierConfigurationBuilder

ID = 'id'
ASSET = 'asset'
CONFIGURATION = 'configuration'
APPROVE = 'approve'
INQUIRE = 'inquire'
FAIL = 'fail'
TEMPLATE = 'template'
TEMPLATE_ID = 'template_id'
ACTIVATION_TILE = 'activation_tile'
EFFECTIVE_DATE = 'effective_date'
MESSAGES = 'messages'
REASON = 'reason'
PARAMS = 'params'
TIER = 'tier'
# connect is always responding with status 400 and error code REQ_003 on all
# bad requests, due to this I need to use the actual error list to match the
# error description instead of the error_code.
ERROR_AS_INVALID_STATUS_TRANSITION_APPROVE = 'Only pending and inquiring requests can be approved.'
ERROR_AS_INVALID_STATUS_TRANSITION_FAIL = 'Only pending requests can be failed.'
ERROR_AS_INVALID_STATUS_TRANSITION_INQUIRE = 'Only pending requests can be moved to inquiring status.'
ERROR_TC_INVALID_TRANSITION_STATUS = 'Tier configuration request status transition is not allowed.'


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
    ) -> RequestBuilder:
        """
        Approves the given request using the given template id.

        :param request: The RequestBuilder object.
        :param template_id: The template id to be used to approve.
        :param activation_tile: The activation tile.
        :param effective_date: The effective date.
        :return: The approved RequestBuilder.
        """
        try:
            payload = {
                TEMPLATE_ID: template_id,
                ACTIVATION_TILE: activation_tile,
                EFFECTIVE_DATE: effective_date,
            }

            request = self.client.requests[request.id()](APPROVE).post(
                payload={k: v for k, v in payload.items() if v is not None},
            )
            return RequestBuilder(request)
        except ClientError as e:
            # REQ_003 - Only pending and inquiring requests can be approved.
            if ERROR_AS_INVALID_STATUS_TRANSITION_APPROVE in e.errors:
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
            if ERROR_AS_INVALID_STATUS_TRANSITION_FAIL in e.errors:
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
            if ERROR_AS_INVALID_STATUS_TRANSITION_INQUIRE in e.errors:
                return request
            raise

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
        if len(difference) > 0:
            request = RequestBuilder(self.client.requests[request.id()].update(
                payload={ASSET: {PARAMS: difference}},
            ))

        return request


class WithTierConfigurationHelper:
    client: Union[ConnectClient, AsyncConnectClient]

    def find_tier_configuration(self, tier_configuration_id: str) -> TierConfigurationBuilder:
        """
        Retrieve a tier configuration by id.

        :param tier_configuration_id: The tier configuration id.
        :return: The tier configuration dictionary
        """
        return TierConfigurationBuilder(self.client.ns(TIER).configs[tier_configuration_id].get())

    def match_tier_configuration(self, criteria: dict) -> List[dict]:
        """
        Get a list of tier configurations that match the provided criteria.

        The valid criteria parameter is:
            {
                "account.company_name": "...",
                "account.external_id": "...",
                "account.external_uid": "...",
                "account.id": "...",
                "connection.id": "...",
                "connection.type": "...",
                "contract.id": "...",
                "created": "...",
                "id": "...",
                "marketplace.id": "...",
                "marketplace.name": "...",
                "params.id": "...",
                "params.value": "...",
                "product.name": "...",
                "status": "...",
                "tier_level": "...",
                "updated": "...",
                "limit": "...",
                "offset": "...",
            }

        :param criteria: The criteria dictionary
        :return: The list of tier configuration dictionaries
        """
        resource = self.client.ns(TIER).configs
        if len(criteria.items()) > 0:
            resource = resource.filter(**{k: v for k, v in criteria.items() if v is not None})

        return list(resource.all())

    def find_tier_configuration_request(self, request_id: str) -> RequestBuilder:
        """
        Retrieve a tier configuration by id.

        :param request_id: The tier configuration request id.
        :return: The tier configuration request dictionary
        """
        return RequestBuilder(self.client.ns(TIER).config_requests[request_id].get())

    def match_tier_configuration_request(self, criteria: dict) -> List[dict]:
        """
        Get a list of tier configuration requests that match the provided criteria.

        :param criteria: The criteria dictionary
        :return: The list of tier configuration request dictionaries
        """
        resource = self.client.ns(TIER).config_requests
        if len(criteria.items()) > 0:
            resource = resource.filter(**{k: v for k, v in criteria.items() if v is not None})

        return list(resource.all())

    def approve_tier_configuration_request(
            self,
            request: RequestBuilder,
            template_id: str,
            effective_date: Optional[str] = None,
    ) -> RequestBuilder:
        """
        Approves the given request using the given template id.

        :param request: The RequestBuilder object.
        :param template_id: The template id to be used to approve.
        :param effective_date: The effective date.
        :return: The approved RequestBuilder.
        """
        try:
            payload = {
                ID: template_id,
                EFFECTIVE_DATE: effective_date,
            }

            request = self.client.ns(TIER).config_requests[request.id()](APPROVE).post(
                payload={TEMPLATE: {k: v for k, v in payload.items() if v is not None}},
            )
            return RequestBuilder(request)
        except ClientError as e:
            # TC_006 - Tier configuration request status transition is not allowed.
            if ERROR_TC_INVALID_TRANSITION_STATUS in e.errors:
                return request
            raise

    def fail_tier_configuration_request(self, request: RequestBuilder, reason: str) -> RequestBuilder:
        """
        Fail the given tier configuration request using the given reason.

        :param request: The RequestBuilder object.
        :param reason: The reason to fail the request.
        :return: The failed RequestBuilder.
        """
        try:
            request = self.client.ns(TIER).config_requests[request.id()](FAIL).post(
                payload={REASON: reason},
            )
            return RequestBuilder(request)
        except ClientError as e:
            # TC_006 - Tier configuration request status transition is not allowed.
            if ERROR_TC_INVALID_TRANSITION_STATUS in e.errors:
                return request
            raise

    def inquire_tier_configuration_request(self, request: RequestBuilder) -> RequestBuilder:
        """
        Inquire the given request.

        :param request: The RequestBuilder object.
        :return: The inquired RequestBuilder.
        """
        try:
            request = self.client.ns(TIER).config_requests[request.id()](INQUIRE).post()
            return RequestBuilder(request)
        except ClientError as e:
            # TC_006 - Tier configuration request status transition is not allowed.
            if ERROR_TC_INVALID_TRANSITION_STATUS in e.errors:
                return request
            raise

    def update_tier_configuration_parameters(self, request: RequestBuilder) -> RequestBuilder:
        """
        Update parameters that have been changed from the given RequestBuilder.

        :param request: The RequestBuilder object.
        :return: The updated RequestBuilder.
        """

        current = self.find_tier_configuration_request(request.id())
        # The tier configuration request parameters are stored in request.params,
        # so in order to compute the difference we must use request.params instead
        # of request.configuration.params. Once the update is done the values will
        # be present in both sections: request.params and request.configuration.params
        params = zip(
            _prepare_parameters(current.params()),
            _prepare_parameters(request.params()),
        )

        difference = [new for cur, new in params if cur != new]
        if len(difference) > 0:
            request = RequestBuilder(self.client.ns(TIER).config_requests[request.id()].update(
                payload={PARAMS: difference},
            ))

        return request


class WithProductHelper:
    client: Union[ConnectClient, AsyncConnectClient]

    def match_product_templates(self, product_id: str, criteria: dict = None) -> List[dict]:
        """
        Get a list of templates by product id that match the provided criteria.

        The valid criteria parameter is:
            {
                "scope": "asset, tier, etc.",
                "type": "inquire, activate, etc."
            }

        :param product_id: The product id from where get the templates.
        :param criteria: The criteria dictionary.
        :return: The list of product templates.
        """
        resource = self.client.products[product_id].templates
        if len(criteria.items()) > 0:
            resource = resource.filter(**{k: v for k, v in criteria.items() if v is not None})

        return list(resource.all())


class WithConversationHelper:
    client: Union[ConnectClient, AsyncConnectClient]

    def match_conversations(self, criteria: dict) -> List[dict]:
        """
        Get a list of conversations that match the provided criteria.

        The valid criteria parameters:
            {
                "id": "the conversation id"
                "instance_id": "the request id"
                "created": "created at time: 2009-05-12T21:58:03.835Z"
                "events.created.id": "events created at time: 2009-05-12T21:58:03.835Z"
                "limit": "number of max conversation per page"
                "offset": "page number offset"
            }

        :param criteria: The criteria dictionary.
        :return: List[str] The list of conversations.
        """
        resource = self.client.conversations
        if len(criteria.items()) > 0:
            resource = resource.filter(**{k: v for k, v in criteria.items() if v is not None})

        return list(resource.all())

    def find_conversation(self, conversation_id: str) -> dict:
        """
        Retrieve a conversation by id.

        :param conversation_id: The conversation id
        :return: The conversation dictionary
        """
        return self.client.conversations[conversation_id].get()

    def add_conversation_message_by_request_id(self, request_id: str, message: str) -> dict:
        """
        Adds a new message to the first conversation by request id (instance id).

        :param request_id: The request id
        :param message: The message to add to the conversation
        :return: The message dictionary
        """
        conversations = self.match_conversations({'instance_id': request_id})
        if len(conversations) == 0:
            raise ValueError('Conversation list is empty.')

        return self.client.conversations[conversations[0]['id']](MESSAGES).post(
            payload={"text": message},
        )
