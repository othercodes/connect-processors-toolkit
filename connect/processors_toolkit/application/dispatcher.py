#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from logging import LoggerAdapter
from typing import Callable, Dict, Type, Union

from connect.eaas.extension import (
    CustomEventResponse,
    ProcessingResponse,
    ProductActionResponse,
    ScheduledExecutionResponse,
    ValidationResponse,
)
from connect.processors_toolkit.application.container import DependencyBuildingFailure
from connect.processors_toolkit.application.router import Route, Router
from connect.processors_toolkit.requests.exceptions import MissingParameterError
from connect.processors_toolkit.logger.mixins import WithBoundedLogger
from connect.processors_toolkit.application import Container
from connect.processors_toolkit.application.contracts import (
    CustomEventTransaction,
    ProcessingTransaction,
    ProductActionTransaction,
    ScheduledTransaction,
    ValidationTransaction,
)
from connect.processors_toolkit.requests import request_model, RequestBuilder

Controller = Union[
    ProcessingTransaction,
    ValidationTransaction,
    CustomEventTransaction,
    ProductActionTransaction,
    ScheduledTransaction,
]

TaskResponse = Union[
    ProcessingResponse,
    ValidationResponse,
    ProductActionResponse,
    CustomEventResponse,
    ScheduledExecutionResponse,
]


class WithDispatcher:
    """
    Dispatch the incoming request to the correct flow controller class based in the
    request parameters.

    If the controller cannot be matched with any of the registered ones the router
    returns a default ProductCustomEventNotFound controller that will respond with
    a 404 http error to the client.
    """
    logger: LoggerAdapter
    container: Container

    def routes(self) -> Dict[str, Type]:
        """
        Maps the product flow controllers by:
            <scope>.<process-type>.<process-name> and <Class Type>.

        - The available scope types are: asset, tier-config, product.
        - The available process types are: process, validate, custom-event, action and schedule.
        - The available process names are:
            - Any request type: purchase, change, suspend, cancel, etc.
            - Any valid string (no spaces allowed) that identifies a custom
            event, product action or schedule process.

        Example:
        {
            'asset.process.purchase': PurchaseFlow,
            'asset.process.change': ChangeFlow,
            'asset.process.cancel': CancelFlow,
            'tier-config.process.setup': ValidatePurchaseFlow,
            'asset.validate.purchase': ValidatePurchaseFlow,
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

        - The available scope types are: asset, tier-config, product.
        - The available process types are: process, validate, custom-event and action.

        Default values:
        {
            'asset.process': ProcessNotFound,
            'tier-config.process': ProcessNotFound,
            'asset.validate': ValidationNotFound,
            'product.custom-event': CustomEventNotFound,
            'product.action': ActionNotFound,
            'product.schedule': ScheduledNotFound,
        }

        :return: The route dictionary.
        """
        return {}

    def __make(self, controller: Type, request: dict) -> Controller:
        instance = self.container.get(controller)
        if issubclass(controller, WithBoundedLogger):
            instance.bind_logger(request)

        return instance

    def __dispatch(
            self,
            request: dict,
            execution_type: str,
            route: Route,
            on_bootstrap_error: Callable[[Exception, dict], TaskResponse],
            execute: Callable[[Controller, dict], TaskResponse],
    ) -> TaskResponse:
        self.logger.debug(f"Processing {execution_type}: {request}")

        controller = Router(self.routes(), self.not_found()).route(route)

        try:
            self.logger.debug(f"Loading {controller} {execution_type} controller.")
            instance = self.__make(controller, request)

        except (MissingParameterError, DependencyBuildingFailure) as e:
            self.logger.error("{error} on bootstrapping controller {controller} due to {msg}".format(
                error=e.__class__.__name__,
                controller=controller,
                msg=str(e),
            ))
            return on_bootstrap_error(e, request)

        self.logger.debug(f"Dispatching {execution_type} using {controller} controller.")
        return execute(instance, request)

    def dispatch_process(self, request: dict, reschedule_time: int = 3600) -> ProcessingResponse:
        return self.__dispatch(
            request,
            'request',
            Route.for_process(request_model(request), request.get('type')),
            # If the controller cannot be instantiated due to missing parameters or
            # dependency building issues, we just need to reschedule the request.
            lambda _, __: ProcessingResponse.slow_process_reschedule(countdown=reschedule_time),
            lambda ctrl, req: ctrl.process(RequestBuilder(req)),
        )

    def dispatch_validation(self, request: dict) -> ValidationResponse:
        return self.__dispatch(
            request,
            'validation',
            Route.for_validate(request_model(request), request.get('type')),
            # If the dynamic validation cannot be executed successfully due to controller
            # instantiation issues, just return the actual request assuming the ordering
            # parameters are valid, the actual purchase, change, etc. process will inquire
            # the request if there are some problem with the parameters.
            lambda _, __: ValidationResponse.done(request),
            lambda ctrl, req: ctrl.validate(RequestBuilder(req)),
        )

    def dispatch_action(self, request: dict) -> ProductActionResponse:
        return self.__dispatch(
            request,
            'action',
            Route.for_action(request.get('jwt_payload', {}).get('action_id')),
            # Return a 500 status code on controller instantiation.
            lambda _, __: ProductActionResponse.done(http_status=500),
            lambda ctrl, req: ctrl.handle(req),
        )

    def dispatch_custom_event(self, request: dict) -> CustomEventResponse:
        return self.__dispatch(
            request,
            'custom event',
            Route.for_custom_event(request.get('body', {}).get('controller')),
            # Return a 500 status code on controller instantiation.
            lambda _, __: CustomEventResponse.done(http_status=500),
            lambda ctrl, req: ctrl.handle(req),
        )

    def dispatch_schedule_process(self, request: dict, schedule_task: str) -> ScheduledExecutionResponse:
        return self.__dispatch(
            request,
            'schedule',
            Route.for_schedule(schedule_task),
            lambda _, __: ScheduledExecutionResponse.done(),
            lambda ctrl, req: ctrl.handle(req),
        )
