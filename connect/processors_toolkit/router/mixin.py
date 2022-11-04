#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from logging import LoggerAdapter
from typing import Callable, Dict, Type, Union

from connect.eaas.extension import CustomEventResponse, ProductActionResponse
from connect.processors_toolkit.dependency_injection.container import DependencyBuildingFailure
from connect.processors_toolkit.router import Route, Router
from connect.processors_toolkit.configuration.exceptions import MissingConfigurationParameterError
from connect.processors_toolkit.requests.exceptions import MissingParameterError
from connect.processors_toolkit.logger.mixins import WithBoundedLogger
from connect.processors_toolkit.application import Container
from connect.processors_toolkit.transactions.contracts import (
    CustomEventTransaction,
    ProductActionTransaction,
)

Controller = Union[
    CustomEventTransaction,
    ProductActionTransaction,
]

Response = Union[
    ProductActionResponse,
    CustomEventResponse,
]


class WithRouter:
    """
    Route the incoming request to the correct product action or custom event
    controller based in the request parameters.

    If the controller cannot be matched with any of the registered ones the router
    returns a default ProductActionNotFound or CustomEventNotFound controller that
    will respond with a 404 http error to the client.
    """
    logger: LoggerAdapter
    container: Container

    def routes(self) -> Dict[str, Type]:
        """
        Maps the product flow controllers by:
            <scope>.<process-type>.<process-name> and <Class Type>.

        - The available scope types are: product.
        - The available process types are: custom-event, action.
        - The available process names are: Any valid string (no spaces allowed)
            that identifies a custom event, product action or schedule process.

        Example:
        {
            'product.custom-event.say-hello': SayHelloCustomEventFlow,
            'product.action.sso': SSOActionFlow,
            'product.schedule.refresh-token': RefreshTokenScheduleFlow,
        }

        :return: The route dictionary.
        """
        return {}

    def not_found(self) -> Dict[str, Type]:
        """
        Maps the product flow controllers for 404 not found:
            <scope>.<process-type> and <Class Type>.

        - The available scope types are: product.
        - The available process types are: custom-event and action.

        Default values:
        {
            'product.custom-event': CustomEventNotFound,
            'product.action': ProductActionNotFound,
            'product.schedule': ScheduledNotFound,
        }

        :return: The route dictionary.
        """
        return {}

    def __route_and_dispatch(
            self,
            request: dict,
            execution_type: str,
            route: Route,
            on_bootstrap_error: Callable[[Exception, dict], Response],
            execute: Callable[[Controller, dict], Response],
    ) -> Response:
        self.logger.debug(f"Processing {execution_type}: {request}")

        controller = Router(self.routes(), self.not_found()).route(route)

        try:
            self.logger.debug(f"Loading {controller} {execution_type} controller.")

            instance = self.container.get(controller)
            if issubclass(controller, WithBoundedLogger):
                instance.bind_logger(request)

        except (MissingParameterError, MissingConfigurationParameterError, DependencyBuildingFailure) as e:
            self.logger.error("{error} on bootstrapping controller {controller} due to {msg}".format(
                error=e.__class__.__name__,
                controller=controller,
                msg=str(e),
            ))
            return on_bootstrap_error(e, request)

        self.logger.debug(f"Dispatching {execution_type} using {controller} controller.")
        return execute(instance, request)

    def route_and_dispatch_product_action(self, request: dict) -> ProductActionResponse:
        return self.__route_and_dispatch(
            request,
            'product action',
            Route.for_action(request.get('jwt_payload', {}).get('action_id')),
            # Return a 500 status code on controller instantiation.
            lambda _, __: ProductActionResponse.done(http_status=500),
            lambda ctrl, req: ctrl.handle(req),
        )

    def route_and_dispatch_custom_event(self, request: dict) -> CustomEventResponse:
        return self.__route_and_dispatch(
            request,
            'custom event',
            Route.for_custom_event(request.get('body', {}).get('controller')),
            # Return a 500 status code on controller instantiation.
            lambda _, __: CustomEventResponse.done(http_status=500),
            lambda ctrl, req: ctrl.handle(req),
        )
