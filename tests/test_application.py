from connect.eaas.extension import ProcessingResponse

from connect.processors_toolkit.application import Application, ProcessingFlow, Dependencies
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
    flow = extension.make(SampleFlow)

    assert isinstance(flow, SampleFlow)
    assert isinstance(flow, ProcessingFlow)


def test_application_should_make_required_flow_controller_with_custom_dependencies(sync_client_factory, logger):
    class MyExtensionWithDependencies(Application):
        def dependencies(self) -> Dependencies:
            return Dependencies().to_class('api', SomeAPIClient)

    class SomeAPIClient:
        pass

    class SampleFlowWithService(ProcessingFlow):
        def __init__(self, api):
            self.api = api

        def process(self, request: RequestBuilder) -> ProcessingResponse:
            return ProcessingResponse.done()

    client = sync_client_factory([])

    extension = MyExtensionWithDependencies(client, logger, {'key': 'value'})
    flow = extension.make(SampleFlowWithService)

    assert isinstance(flow, SampleFlowWithService)
    assert isinstance(flow, ProcessingFlow)
