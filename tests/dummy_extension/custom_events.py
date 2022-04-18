from connect.eaas.extension import CustomEventResponse
from connect.processors_toolkit.application.contracts import CustomEventFlow


class HelloWorld(CustomEventFlow):
    def __init__(self, logger, config, my_app_name):
        self.logger = logger
        self.config = config
        self.app_name = my_app_name

    def handle(self, request: dict) -> CustomEventResponse:
        self.logger.info('Just printing a hello message!')

        return CustomEventResponse.done(
            http_status=200,
            body=f"Hello from {self.app_name}",
        )
