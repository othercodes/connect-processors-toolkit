from logging import LoggerAdapter
from typing import Callable
from unittest.mock import Mock

from connect.processors_toolkit.logger import ExtensionLoggerAdapter
from connect.processors_toolkit.logger.mixins import WithBoundedLogger
from connect.processors_toolkit.requests import RequestBuilder


def make_fake_logger(assertion: Callable):
    def _assert_log(msg):
        assert assertion

    logger = Mock()
    logger.info = _assert_log

    return logger


class Helper(WithBoundedLogger):
    def __init__(self, logger: LoggerAdapter):
        self.logger = logger


def test_bounded_logger_should_configure_logger_from_request_dictionary():
    helper = Helper(LoggerAdapter(Mock(), {}))
    helper.bind_logger({'id': 'PR-123-456-789'})

    assert 'id' in helper.logger.extra
    assert helper.logger.extra.get('id') == 'PR-123-456-789'


def test_bounded_logger_should_configure_logger_from_request_builder():
    helper = Helper(LoggerAdapter(Mock(), {}))
    helper.bind_logger(RequestBuilder({'id': 'PR-123-456-789'}))

    assert 'id' in helper.logger.extra
    assert helper.logger.extra.get('id') == 'PR-123-456-789'


def test_bounded_logger_should_not_configure_logger_from_invalid_request():
    helper = Helper(LoggerAdapter(Mock(), {}))
    helper.bind_logger('Some invalid request')

    assert 'id' not in helper.logger.extra


def test_logger_should_attach_id_to_message_if_configured():
    message = 'This is a cool log message'

    logger = ExtensionLoggerAdapter(
        make_fake_logger(lambda msg: msg == f'SOME-ID {message}'),
        {'id': 'SOME-ID'},
    )

    logger.info(message)


def test_logger_should_not_attach_id_to_message_if_not_configured():
    message = 'Hello world from the logger'

    logger = ExtensionLoggerAdapter(
        make_fake_logger(lambda msg: msg == message),
        {},
    )

    logger.info(message)
