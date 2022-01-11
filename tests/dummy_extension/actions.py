from connect.eaas.extension import ProductActionResponse
from connect.processors_toolkit.application.contracts import ProductActionFlow


class SSO(ProductActionFlow):
    def __init__(self, logger):
        self.logger = logger

    def handle(self, request: dict) -> ProductActionResponse:
        self.logger.info('Doing Single-Sign-On on Google!')

        return ProductActionResponse.done(
            http_status=302,
            headers={'Location': 'https://google.com'},
        )
