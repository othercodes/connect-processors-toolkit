from connect.eaas.extension import ScheduledExecutionResponse
from connect.processors_toolkit.transactions.contracts import ScheduledTransaction


class RefreshToken(ScheduledTransaction):
    def __init__(self, logger):
        self.logger = logger

    def handle(self, request: dict) -> ScheduledExecutionResponse:
        self.logger.info('Refreshing the token on product!')

        return ScheduledExecutionResponse.done()
