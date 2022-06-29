from __future__ import annotations

from dataclasses import dataclass
from logging import LoggerAdapter
from typing import Dict, Type, Union

from connect.eaas.extension import (
    CustomEventResponse,
    ProcessingResponse,
    ProductActionResponse,
    ValidationResponse,
)
from connect.processors_toolkit.application.container import DependencyBuildingFailure
from connect.processors_toolkit.requests.exceptions import MissingParameterError
from connect.processors_toolkit.logger.mixins import WithBoundedLogger
from connect.processors_toolkit.application import Container
from connect.processors_toolkit.application.contracts import (
    CustomEventFlow,
    ProcessingFlow,
    ProductActionFlow,
    ValidationFlow,
)
from connect.processors_toolkit.requests import request_model, RequestBuilder

ERROR_CONTROLLER_BOOTSTRAP = "{error} on bootstrapping controller {controller} due to {msg}"


class _ProcessFlowNotFound(ProcessingFlow):
    def process(self, request: RequestBuilder) -> ProcessingResponse:
        """
        Handles the request in the case no flow controller match.

        :param request:
        :return: ProcessingResponse
        """
        raise NotImplementedError()


class _ValidationFlowNotFound(ValidationFlow):
    def validate(self, request: RequestBuilder) -> ValidationResponse:
        """
        Handles the request in the case no flow controller match.

        :param request:
        :return: ValidationResponse
        """
        raise NotImplementedError()


class _CustomEventFlowNotFound(CustomEventFlow):
    def handle(self, request: dict) -> CustomEventResponse:
        """
        Handles the request in case no flow controller match.

        :param request:
        :return: CustomEventResponse
        """
        return CustomEventResponse.done(http_status=404)


class _ActionFlowNotFound(ProductActionFlow):
    def handle(self, request: dict) -> ProductActionResponse:
        """
        Handles the request in case no flow controller match.

        :param request:
        :return: ProductActionResponse
        """
        return ProductActionResponse.done(http_status=404)


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

    def __post_init__(self):
        if self.scope not in [self.SCOPE_ASSET, self.SCOPE_TIER_CONFIG, self.SCOPE_PRODUCT]:
            raise ValueError(f'Invalid route scope value <{self.scope}>.')

        if self.process not in [self.PROCESS_PROCESS, self.PROCESS_VALIDATE,
                                self.PROCESS_CUSTOM_EVENT, self.PROCESS_ACTION]:
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
    def for_custom_event(scope: str, action: str) -> Route:
        return Route(scope, Route.PROCESS_CUSTOM_EVENT, action)

    @staticmethod
    def for_action(scope: str, action: str) -> Route:
        return Route(scope, Route.PROCESS_ACTION, action)

    def not_found(self) -> str:
        return f"{self.scope}.{self.process}"

    def main(self) -> str:
        return f"{self.scope}.{self.process}.{self.name}"


Controller = Union[ProcessingFlow, ValidationFlow, CustomEventFlow, ProductActionFlow]


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
        - The available process types are: process, validate, custom-event and action.
        - The available process names are:
            - Any request type: purchase, change, suspend, cancel, etc.
            - Any valid string (no spaces allowed) that identifies a custom
            event or a product action.

        Example:
        {
            'asset.process.purchase': PurchaseFlow,
            'asset.process.change': ChangeFlow,
            'asset.process.cancel': CancelFlow,
            'tier-config.process.setup': ValidatePurchaseFlow,
            'asset.validate.purchase': ValidatePurchaseFlow,
            'product.custom-event.say-hello': SayHelloCustomEventFlow,
            'product.action.sso': SSOActionFlow,
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
            'asset.process': _ProcessFlowNotFound,
            'tier-config.process': _ProcessFlowNotFound,
            'asset.validate': ValidatePurchaseFlow,
            'product.custom-event': _CustomEventFlowNotFound,
            'product.action': _ActionFlowNotFound,
        }

        :return: The route dictionary.
        """
        return {}

    def _route(self, route: Route, not_found_controller: Type) -> Type:
        controller = self.routes().get(route.main())
        if controller is None:
            controller = self.not_found().get(route.not_found(), not_found_controller)

        return controller

    def _make(self, controller: Type, request: dict) -> Controller:
        instance = self.container.get(controller)
        if issubclass(controller, WithBoundedLogger):
            instance.bind_logger(request)

        return instance

    def dispatch_process(self, request: dict, reschedule_time: int = 3600) -> ProcessingResponse:
        self.logger.debug(f"Processing request: {request}")

        controller = self._route(
            Route.for_process(request_model(request), request.get('type')),
            _ProcessFlowNotFound,
        )

        self.logger.debug(f"Dispatching request using {controller} controller.")

        try:
            instance = self._make(controller, request)
        except (MissingParameterError, DependencyBuildingFailure) as e:
            self.logger.error(ERROR_CONTROLLER_BOOTSTRAP.format(
                error=e.__class__.__name__,
                controller=controller,
                msg=str(e),
            ))
            # If the controller cannot be instantiated due to missing parameters or
            # dependency building issues, we just need to reschedule the request.
            return ProcessingResponse.slow_process_reschedule(countdown=reschedule_time)

        return instance.process(RequestBuilder(request))

    def dispatch_validation(self, request: dict) -> ValidationResponse:
        self.logger.debug(f"Validating request: {request}")

        controller = self._route(
            Route.for_validate(request_model(request), request.get('type')),
            _ValidationFlowNotFound,
        )

        self.logger.debug(f"Validating request using {controller} controller.")

        try:
            instance = self._make(controller, request)
        except (MissingParameterError, DependencyBuildingFailure) as e:
            self.logger.error(ERROR_CONTROLLER_BOOTSTRAP.format(
                error=e.__class__.__name__,
                controller=controller,
                msg=str(e),
            ))
            # If the dynamic validation cannot be executed successfully due to controller
            # instantiation issues, just return the actual request assuming the ordering
            # parameters are valid, the actual purchase, change, etc. process will inquire
            # the request if there are some problem with the parameters.
            return ValidationResponse.done(request)

        return instance.validate(RequestBuilder(request))

    def dispatch_action(self, request: dict) -> ProductActionResponse:
        self.logger.debug(f"Processing name: {request}")

        controller = self._route(
            Route.for_action('product', request.get('jwt_payload', {}).get('action_id')),
            _ActionFlowNotFound,
        )

        self.logger.debug(f"Dispatching action using {controller} controller.")

        try:
            instance = self._make(controller, request)
        except (MissingParameterError, DependencyBuildingFailure) as e:
            self.logger.error(ERROR_CONTROLLER_BOOTSTRAP.format(
                error=e.__class__.__name__,
                controller=controller,
                msg=str(e),
            ))
            # Return a 500 status code on controller instantiation.
            return ProductActionResponse.done(http_status=500)

        return instance.handle(request)

    def dispatch_custom_event(self, request: dict) -> CustomEventResponse:
        self.logger.debug(f"Processing custom event: {request}")

        controller = self._route(
            Route.for_custom_event('product', request.get('body', {}).get('controller')),
            _CustomEventFlowNotFound,
        )

        self.logger.debug(f"Dispatching custom event using {controller} controller.")

        try:
            instance = self._make(controller, request)
        except (MissingParameterError, DependencyBuildingFailure) as e:
            self.logger.error(ERROR_CONTROLLER_BOOTSTRAP.format(
                error=e.__class__.__name__,
                controller=controller,
                msg=str(e),
            ))
            # Return a 500 status code on controller instantiation.
            return CustomEventResponse.done(http_status=500)

        return instance.handle(request)
