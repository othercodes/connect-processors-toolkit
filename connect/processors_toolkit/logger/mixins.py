from logging import LoggerAdapter
from typing import Union

from connect.processors_toolkit.logger import ExtensionLoggerAdapter
from connect.processors_toolkit.requests import RequestBuilder


class WithBoundedLogger:
    logger: LoggerAdapter

    def bind_logger(self, request: Union[RequestBuilder, dict]) -> LoggerAdapter:
        """
        Binds the logger to the given request by attaching the id to
        the extra data of the logger adapter.

        :param request: Union[RequestBuilder, dict] The request to extract the ids
        :return: LoggerAdapter
        """
        from_request = {}
        if isinstance(request, RequestBuilder) and request.id() is not None:
            from_request.update({'id': request.id()})

        elif isinstance(request, dict) and request.get('id') is not None:
            from_request.update({'id': request.get('id')})

        self.logger = ExtensionLoggerAdapter(
            self.logger.logger,
            {**self.logger.extra, **from_request},
        )
        return self.logger
