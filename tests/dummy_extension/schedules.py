from connect.eaas.extension import ScheduledExecutionResponse
from connect.processors_toolkit.application.contracts import ScheduledFlow


class RefreshToken(ScheduledFlow):
    def __init__(self, logger):
        self.logger = logger

    def handle(self, request: dict) -> ScheduledExecutionResponse:
        self.logger.info('Refreshing the token on product!')

        return ScheduledExecutionResponse.done()
