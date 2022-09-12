#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Type, Union

from connect.eaas.core.responses import (
    CustomEventResponse,
    ProcessingResponse,
    ProductActionResponse,
    ScheduledExecutionResponse,
    ValidationResponse,
)
from connect.processors_toolkit.application.contracts import (
    CustomEventTransaction,
    ProcessingTransaction,
    ProductActionTransaction,
    ScheduledTransaction,
    ValidationTransaction,
)
from connect.processors_toolkit.requests import RequestBuilder


class ProcessNotFound(ProcessingTransaction):
    def process(self, request: Union[RequestBuilder, dict]) -> ProcessingResponse:
        """
        Handles the request in the case no flow controller match.

        :param request:
        :return: ProcessingResponse
        """
        raise NotImplementedError()


class ValidationNotFound(ValidationTransaction):
    def validate(self, request: Union[RequestBuilder, dict]) -> ValidationResponse:
        """
        Handles the request in the case no flow controller match.

        :param request:
        :return: ValidationResponse
        """
        raise NotImplementedError()


class CustomEventNotFound(CustomEventTransaction):
    def handle(self, request: dict) -> CustomEventResponse:
        """
        Handles the request in case no flow controller match.

        :param request:
        :return: CustomEventResponse
        """
        return CustomEventResponse.done(http_status=404)


class ActionNotFound(ProductActionTransaction):
    def handle(self, request: dict) -> ProductActionResponse:
        """
        Handles the request in case no flow controller match.

        :param request:
        :return: ProductActionResponse
        """
        return ProductActionResponse.done(http_status=404)


class ScheduledNotFound(ScheduledTransaction):
    def handle(self, request: dict) -> ScheduledExecutionResponse:
        """
        Handles the request in the case no flow controller match.

        :param request:
        :return: ScheduledExecutionResponse
        """
        raise NotImplementedError()


@dataclass
class Route:
    scope: str
    process: str
    name: str

    SCOPE_ASSET = 'asset'
    SCOPE_TIER_CONFIG = 'tier-config'
    SCOPE_PRODUCT = 'product'

    PROCESS_PROCESS = 'process'
    PROCESS_VALIDATE = 'validate'
    PROCESS_CUSTOM_EVENT = 'custom-event'
    PROCESS_ACTION = 'action'
    PROCESS_SCHEDULE = 'schedule'

    def __post_init__(self):
        if self.scope not in self.scopes():
            raise ValueError(f'Invalid route scope value <{self.scope}>.')

        if self.process not in self.processes():
            raise ValueError(f'Invalid route process value <{self.process}>.')

        if ' ' in self.name:
            raise ValueError('Invalid route name, must not contains spaces.')

    @staticmethod
    def for_process(scope: str, action: str) -> Route:
        return Route(scope, Route.PROCESS_PROCESS, action)

    @staticmethod
    def for_validate(scope: str, action: str) -> Route:
        return Route(scope, Route.PROCESS_VALIDATE, action)

    @staticmethod
    def for_custom_event(action: str) -> Route:
        return Route(Route.SCOPE_PRODUCT, Route.PROCESS_CUSTOM_EVENT, action)

    @staticmethod
    def for_action(action: str) -> Route:
        return Route(Route.SCOPE_PRODUCT, Route.PROCESS_ACTION, action)

    @staticmethod
    def for_schedule(action: str) -> Route:
        return Route(Route.SCOPE_PRODUCT, Route.PROCESS_SCHEDULE, action)

    def scopes(self) -> List[str]:
        return [
            self.SCOPE_ASSET,
            self.SCOPE_TIER_CONFIG,
            self.SCOPE_PRODUCT,
        ]

    def processes(self) -> List[str]:
        return [
            self.PROCESS_PROCESS,
            self.PROCESS_VALIDATE,
            self.PROCESS_CUSTOM_EVENT,
            self.PROCESS_ACTION,
            self.PROCESS_SCHEDULE,
        ]

    def not_found(self) -> str:
        return f"{self.scope}.{self.process}"

    def main(self) -> str:
        return f"{self.scope}.{self.process}.{self.name}"


class Router:
    def __init__(self, routes: Dict[str, Type], not_found: Dict[str, Type]):
        self.__routes: Dict[str, Type] = routes
        self.__not_found: Dict[str, Type] = {
            'asset.process': ProcessNotFound,
            'tier-config.process': ProcessNotFound,
            'asset.validate': ValidationNotFound,
            'product.custom-event': CustomEventNotFound,
            'product.action': ActionNotFound,
            'product.schedule': ScheduledNotFound,
        }

        self.__not_found.update(not_found)

    def route(self, route: Route) -> Type:
        controller = self.__routes.get(route.main())
        if controller is None:
            controller = self.__not_found.get(route.not_found())

        return controller
