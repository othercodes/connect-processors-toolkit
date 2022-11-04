#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from logging import LoggerAdapter
from typing import Callable, List, Optional, Union

from connect.client import AsyncConnectClient, ConnectClient
from connect.eaas.core.responses import ProcessingResponse
from connect.processors_toolkit.api.mixins import WithAssetHelper
from connect.processors_toolkit.offline.contracts import OfflineChecker
from connect.processors_toolkit.requests import MissingParameterError, RequestBuilder
from connect.processors_toolkit.transactions.contracts import FnProcessingTransaction

Rule = Callable[[dict], bool]

PARAM_OFFLINE_MODE_LIST = 'offline_mode_list'
PARAM_OFFLINE_MODE = 'offline_mode'


def match_request_type(request: dict) -> bool:
    return RequestBuilder(request).type() in ['cancel', 'suspend']


def match_offline_asset_parameter(request: dict) -> bool:
    """
    Evaluate if the given connect request is in offline mode based on
    the offline_mode asset ordering parameter.

    :param request: dict The Connect request dictionary.
    :return: bool
    """
    request = RequestBuilder(request)

    # Ordering parameters can be found:
    #   a. in the request business object.
    #   b. in the request asset business object.

    offline_mode_list = []
    try:
        # First, try to extract the value from request parameters.
        offline_mode_list.append(request.param(PARAM_OFFLINE_MODE, 'value', ''))
    except MissingParameterError:
        pass

    try:
        # Next, try to extract the value from the request asset parameters.
        offline_mode_list.append(request.asset().asset_param(PARAM_OFFLINE_MODE, 'value', ''))
    except MissingParameterError:
        pass

    # finally evaluate if the subscription id (asset id) is in the list.
    return request.asset().asset_id() in offline_mode_list


def match_offline_marketplace_parameter(request: dict) -> bool:
    """
    Evaluate if the given connect request is in offline mode based on
    the offline_mode_list marketplace configuration parameter.

    :param request: dict The Connect request dictionary.
    :return: bool
    """
    request = RequestBuilder(request)
    try:
        offline_mode_list = request.asset().asset_configuration_param(
            PARAM_OFFLINE_MODE_LIST,
            'structured_value',
            [],
        )
        return request.asset().asset_id() in offline_mode_list
    except MissingParameterError:
        return False


def composited_match_offline_asset_and_marketplace_parameter(request: dict) -> bool:
    """
    Composite rule
    :param request:
    :return:
    """
    return any([
        match_offline_marketplace_parameter(request),
        match_offline_asset_parameter(request),
    ])


class DefaultOnMatchTransaction(WithAssetHelper):
    def __init__(self, activation_tpl: str, client: Union[ConnectClient, AsyncConnectClient], logger: LoggerAdapter):
        self.activation_tpl = activation_tpl
        self.client = client
        self.logger = logger

    def __call__(self, request: dict) -> ProcessingResponse:
        request = RequestBuilder(request)
        self.logger.info("The subscription {id} is in offline mode.".format(
            id=request.asset().asset_id(),
        ))
        self.approve_asset_request(request, self.activation_tpl)

        return ProcessingResponse.done()


class OfflineCriteria(OfflineChecker):
    def __init__(self, criteria: List[Rule], on_match: Optional[FnProcessingTransaction] = None):
        self.__criteria = criteria
        self.__on_match = on_match

    def is_offline_enabled(self, request: dict) -> bool:
        if len(self.__criteria) == 0:
            return False

        for rule in self.__criteria:
            if not rule(request):
                return False

        return True

    def __call__(self, request: dict, nxt: Optional[FnProcessingTransaction] = None) -> ProcessingResponse:
        """
        Middleware implementation of the offline mode

        :param request: dict The Connect Request dict.
        :param nxt: Optional[FnTransaction] The optional next middleware (Functional Transaction).
        :return: ProcessingResponse
        """
        if not self.is_offline_enabled(request):
            return nxt(request)

        if callable(self.__on_match):
            return self.__on_match(request)
        return ProcessingResponse.skip()
