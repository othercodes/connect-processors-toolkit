from typing import Dict

import pytest

from connect.processors_toolkit.configuration.exceptions import MissingConfigurationParameterError
from connect.processors_toolkit.configuration.mixins import WithConfigurationHelper


class Helper(WithConfigurationHelper):
    def __init__(self, config: Dict[str, str]):
        self.config = config


def test_configuration_helper_should_retrieve_the_request_configuration():
    value = Helper({'CFG_KEY_001': 'CFG_VALUE_001'}).configuration('CFG_KEY_001')

    assert value == 'CFG_VALUE_001'


def test_configuration_helper_should_raise_exception_on_missing_configuration():
    with pytest.raises(MissingConfigurationParameterError):
        Helper({}).configuration('CFG_KEY_001')
