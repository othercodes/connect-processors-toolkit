import pytest
from connect.eaas.extension import ProcessingResponse
from connect.processors_toolkit.application import Application, Dependencies, DependencyBuildingFailure
from connect.processors_toolkit.application.contracts import ProcessingFlow
from connect.processors_toolkit.requests import RequestBuilder


def test_application_should_make_required_flow_controller(sync_client_factory, logger):
    class MySimpleExtension(Application):
        pass

    class SampleFlow(ProcessingFlow):
        def __init__(self, logger):
            self.logger = logger

        def process(self, request: RequestBuilder) -> ProcessingResponse:
            return ProcessingResponse.done()

    client = sync_client_factory([])

    extension = MySimpleExtension(client, logger, {'key': 'value'})
    flow = extension.container.get(SampleFlow)

    assert isinstance(flow, SampleFlow)
    assert isinstance(flow, ProcessingFlow)


def test_application_should_make_required_flow_controller_with_custom_dependencies(sync_client_factory, logger):
    def provide_complex_value(self):
        return 'my-very-complex-value'

    class MyExtensionWithDependencies(Application):
        def dependencies(self) -> Dependencies:
            return Dependencies() \
                .to_class('api_client', SomeAPIClient) \
                .provider('complex_value', provide_complex_value)

    class SomeAPIClient:
        def __init__(self, api_key, complex_value):
            self.api_key = api_key
            self.complex_value = complex_value

    class SampleFlowWithService(ProcessingFlow):
        def __init__(self, api_client):
            self.api_client = api_client

        def process(self, request: RequestBuilder) -> ProcessingResponse:
            return ProcessingResponse.done()

    client = sync_client_factory([])
    config = {'API_KEY': 'my-secret-api-key'}

    extension = MyExtensionWithDependencies(client, logger, config)
    flow = extension.container.get(SampleFlowWithService)

    assert isinstance(flow, SampleFlowWithService)
    assert isinstance(flow, ProcessingFlow)
    assert flow.api_client.api_key == config['API_KEY']
    assert flow.api_client.complex_value == 'my-very-complex-value'


def test_application_should_raise_exception_on_building_dependencies(sync_client_factory, logger):
    class MyExtensionWithDependencies(Application):
        pass

    class SampleFlowWithService(ProcessingFlow):
        def __init__(self, non_registered_dependency):
            self.non_registered_dependency = non_registered_dependency

        def process(self, request: RequestBuilder) -> ProcessingResponse:
            return ProcessingResponse.done()

    client = sync_client_factory([])
    config = {}

    extension = MyExtensionWithDependencies(client, logger, config)

    with pytest.raises(DependencyBuildingFailure):
        extension.container.get(SampleFlowWithService)
