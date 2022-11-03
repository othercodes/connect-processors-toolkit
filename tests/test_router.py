from typing import Dict, Type

import pytest

from tests.dummy_extension.actions import SSO
from tests.dummy_extension.custom_events import HelloWorld
from tests.dummy_extension.extension import AbstractExtension

from connect.eaas.core.responses import CustomEventResponse, ProductActionResponse
from connect.processors_toolkit.router import Router, Route, CustomEventNotFound


class SampleCustomEvent(CustomEventNotFound):
    def process(self, request: dict) -> CustomEventResponse:
        raise NotImplementedError()


def test_router_should_resolve_successfully_route():
    router = Router(
        {'product.custom-event.sample': SampleCustomEvent},
        {}
    )

    controller = router.route(Route.for_custom_event('sample'))

    assert controller == SampleCustomEvent


def test_router_should_return_not_found_route():
    router = Router({}, {})

    controller = router.route(Route.for_custom_event('not-exists'))

    assert controller == CustomEventNotFound


def test_route_should_raise_exception_on_invalid_arguments():
    with pytest.raises(ValueError):
        Route('invalid', 'process', 'purchase')

    with pytest.raises(ValueError):
        Route('asset', 'invalid', 'purchase')

    with pytest.raises(ValueError):
        Route('asset', 'process', 'not valid')


def test_dispatcher_should_dispatch_custom_event_flow_controller(sync_client_factory, logger):
    client = sync_client_factory([])
    config = {'my_app_name': 'cool-app-name'}

    request = {'body': {'controller': 'hello-world'}}

    class MyDummyExtension(AbstractExtension):
        def routes(self) -> Dict[str, Type]:
            return {
                'product.custom-event.hello-world': HelloWorld,
            }

    extension = MyDummyExtension(client, logger, config)
    response = extension.route_and_dispatch_custom_event(request)

    assert isinstance(response, CustomEventResponse)
    assert response.http_status == 200
    assert response.body == "Hello from cool-app-name"


def test_dispatcher_should_dispatch_custom_event_not_found_controller(sync_client_factory, logger):
    client = sync_client_factory([])
    config = {}

    request = {'body': {'controller': 'unknown-controller'}}

    class MyDummyExtension(AbstractExtension):
        pass

    extension = MyDummyExtension(client, logger, config)
    response = extension.route_and_dispatch_custom_event(request)

    assert isinstance(response, CustomEventResponse)
    assert response.http_status == 404


def test_dispatcher_should_dispatch_action_flow_controller(sync_client_factory, logger):
    client = sync_client_factory([])
    config = {'my_app_name': 'cool-app-name'}

    request = {'jwt_payload': {'action_id': 'sso'}}

    class MyDummyExtension(AbstractExtension):
        def routes(self) -> Dict[str, Type]:
            return {
                'product.action.sso': SSO
            }

    extension = MyDummyExtension(client, logger, config)
    response = extension.route_and_dispatch_product_action(request)

    assert isinstance(response, ProductActionResponse)
    assert response.http_status == 302
    assert response.headers.get('Location') == 'https://google.com'


def test_dispatcher_should_dispatch_action_not_found_controller(sync_client_factory, logger):
    client = sync_client_factory([])
    config = {}

    request = {'jwt_payload': {'action_id': 'unknown-action-id'}}

    class MyDummyExtension(AbstractExtension):
        pass

    extension = MyDummyExtension(client, logger, config)
    response = extension.route_and_dispatch_product_action(request)

    assert isinstance(response, ProductActionResponse)
    assert response.http_status == 404
