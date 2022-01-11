from logging import LoggerAdapter
from typing import Dict

from connect.client import ConnectClient
from connect.eaas.extension import ValidationResponse
from connect.processors_toolkit.application.contracts import ValidationFlow
from connect.processors_toolkit.requests import RequestBuilder


class Purchase(ValidationFlow):
    def __init__(
            self,
            client: ConnectClient,
            logger: LoggerAdapter,
            config: Dict[str, str],
    ):
        self.client = client
        self.logger = logger
        self.config = config

    def validate(self, request: RequestBuilder) -> ValidationResponse:
        self.logger.info('Everything is valid!!!')

        return ValidationResponse.done(data=request.raw())
