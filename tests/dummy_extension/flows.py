from logging import LoggerAdapter
from typing import Dict

from connect.client import ConnectClient
from connect.eaas.extension import ProcessingResponse
from connect.processors_toolkit.logger.mixins import WithBoundedLogger
from connect.processors_toolkit.application.contracts import ProcessingTransaction
from connect.processors_toolkit.requests import RequestBuilder


class Purchase(ProcessingTransaction, WithBoundedLogger):
    def __init__(
            self,
            client: ConnectClient,
            logger: LoggerAdapter,
            config: Dict[str, str],
    ):
        self.client = client
        self.logger = logger
        self.config = config

    def process(self, request: RequestBuilder) -> ProcessingResponse:
        self.logger.info('Auto approve, its free!!')

        return ProcessingResponse.done()
