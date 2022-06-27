from logging import LoggerAdapter
from typing import Union

from connect.processors_toolkit.logger import bind_logger
from connect.processors_toolkit.requests import RequestBuilder


class WithBoundedLogger:
    logger: LoggerAdapter

    def bind_logger(self, request: Union[RequestBuilder, dict]) -> LoggerAdapter:
        self.logger = bind_logger(self.logger, request)
        return self.logger
