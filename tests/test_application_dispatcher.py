from typing import Dict, Type

import pytest

from connect.eaas.extension import CustomEventResponse, ProductActionResponse
from connect.processors_toolkit.application.dispatcher import Route
from connect.processors_toolkit.requests.assets import AssetBuilder
from connect.processors_toolkit.requests import RequestBuilder

from tests.dummy_extension.actions import SSO
from tests.dummy_extension.custom_events import HelloWorld
from tests.dummy_extension.extension import AbstractExtension
from tests.dummy_extension.flows import Purchase as PurchaseFlow
from tests.dummy_extension.schedules import RefreshToken
from tests.dummy_extension.validations import Purchase as PurchaseValidationFlow


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
    response = extension.dispatch_custom_event(request)

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
    response = extension.dispatch_custom_event(request)

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
    response = extension.dispatch_action(request)

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
    response = extension.dispatch_action(request)

    assert isinstance(response, ProductActionResponse)
    assert response.http_status == 404


def test_dispatcher_should_dispatch_validation_flow_controller(sync_client_factory, logger):
    client = sync_client_factory([])
    config = {}

    request = RequestBuilder()
    request.with_id('PR-1234-5678-900-001')
    request.with_type('purchase')
    asset = AssetBuilder()
    asset.with_asset_id('AS-1234-5678-900')
    request.with_asset(asset)

    class MyDummyExtension(AbstractExtension):
        def routes(self) -> Dict[str, Type]:
            return {
                'asset.validate.purchase': PurchaseValidationFlow,
            }

    extension = MyDummyExtension(client, logger, config)
    response = extension.validate_asset_purchase_request(request.raw())

    assert response.data['id'] == 'PR-1234-5678-900-001'


def test_dispatcher_should_dispatch_validation_not_found_flow_controller(sync_client_factory, logger):
    client = sync_client_factory([])
    config = {}

    request = RequestBuilder()
    request.with_id('PR-1234-5678-900-001')
    request.with_type('change')
    asset = AssetBuilder()
    asset.with_asset_id('AS-1234-5678-900')
    request.with_asset(asset)

    class MyDummyExtension(AbstractExtension):
        pass

    extension = MyDummyExtension(client, logger, config)

    with pytest.raises(NotImplementedError):
        extension.validate_asset_purchase_request(request.raw())


def test_dispatcher_should_dispatch_process_flow_controller(sync_client_factory, logger):
    client = sync_client_factory([])
    config = {}

    request = RequestBuilder()
    request.with_id('PR-1234-5678-900-001')
    request.with_type('purchase')
    asset = AssetBuilder()
    asset.with_asset_id('AS-1234-5678-900')
    request.with_asset(asset)

    class MyDummyExtension(AbstractExtension):
        def routes(self) -> Dict[str, Type]:
            return {
                'asset.process.purchase': PurchaseFlow,
            }

    extension = MyDummyExtension(client, logger, config)
    response = extension.process_asset_purchase_request(request.raw())

    assert response.status == 'success'


def test_dispatcher_should_dispatch_process_not_found_flow_controller(sync_client_factory, logger):
    client = sync_client_factory([])
    config = {}

    request = RequestBuilder()
    request.with_id('PR-1234-5678-900-001')
    request.with_type('suspend')
    asset = AssetBuilder()
    asset.with_asset_id('AS-1234-5678-900')
    request.with_asset(asset)

    class MyDummyExtension(AbstractExtension):
        pass

    extension = MyDummyExtension(client, logger, config)

    with pytest.raises(NotImplementedError):
        extension.validate_asset_purchase_request(request.raw())


def test_dispatcher_should_dispatch_schedule_flow_controller(sync_client_factory, logger):
    client = sync_client_factory([])
    config = {}

    request = {"product_id": "PRD-000-000-000"}

    class MyDummyExtension(AbstractExtension):
        def routes(self) -> Dict[str, Type]:
            return {
                'product.schedule.refresh-token': RefreshToken,
            }

    extension = MyDummyExtension(client, logger, config)
    response = extension.execute_refresh_token_schedule(request)

    assert response.status == 'success'


def test_dispatcher_should_dispatch_schedule_not_found_flow_controller(sync_client_factory, logger):
    client = sync_client_factory([])
    config = {}

    class MyDummyExtension(AbstractExtension):
        pass

    extension = MyDummyExtension(client, logger, config)

    with pytest.raises(NotImplementedError):
        extension.execute_refresh_token_schedule({})
