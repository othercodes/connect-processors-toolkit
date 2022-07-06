from typing import Optional


class MissingConfigurationParameterError(Exception):
    def __init__(self, message: str, parameter: Optional[str] = None):
        self.message = message
        self.parameter = parameter

        super().__init__(self.message)
