from typing import Union

from connect.eaas.core.responses import ProcessingResponse

from connect.processors_toolkit.application.contracts import ProcessingTransaction
from connect.processors_toolkit.application.router import Router, ProcessNotFound, Route
from connect.processors_toolkit.requests import RequestBuilder


class SamplePurchaseProcess(ProcessingTransaction):
    def process(self, request: Union[RequestBuilder, dict]) -> ProcessingResponse:
        """
        Handles the request in the case no flow controller match.

        :param request:
        :return: ProcessingResponse
        """
        raise NotImplementedError()


def test_router_should_resolve_successfully_route():
    routes = {'asset.process.purchase': SamplePurchaseProcess}
    not_found = {}
    request = RequestBuilder() \
        .with_asset({}) \
        .with_type('purchase')

    router = Router(routes, not_found)

    controller = router.route(Route.for_process(request.request_type(), request.type()))

    assert controller == SamplePurchaseProcess


def test_router_should_return_not_found_route():
    routes = {}
    not_found = {}
    request = RequestBuilder() \
        .with_asset({}) \
        .with_type('purchase')

    router = Router(routes, not_found)

    controller = router.route(Route.for_process(request.request_type(), request.type()))

    assert controller == ProcessNotFound

