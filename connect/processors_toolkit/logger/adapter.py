from logging import LoggerAdapter
from typing import Union

from connect.processors_toolkit.requests import RequestBuilder


class ExtensionLoggerAdapter(LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra

        if 'request_id' in extra:
            msg = f"{extra.get('request_id')} {msg}"

        return msg, kwargs


def bind_logger(logger: LoggerAdapter, request: Union[RequestBuilder, dict]) -> LoggerAdapter:
    """
    Binds the logger to the given request by attaching the id and some
    additional information to the extra data of the logger adapter.

    :param logger: LoggerAdapter The logger to bind with the request.
    :param request: Union[RequestBuilder, dict] The request to extract the ids.
    :return: LoggerAdapter
    """
    if not isinstance(request, RequestBuilder):
        if not isinstance(request, dict):
            return logger
        request = RequestBuilder(request)

    from_request = {
        'request_id': request.id(),
        'request_type': request.type(),
        'request_status': request.status(),
    }

    if request.is_asset_request():
        from_request['tier_id'] = request.asset().asset_tier_customer('id')
        from_request['asset_id'] = request.asset().asset_id()

    elif request.is_tier_config_request():
        from_request['tier_id'] = request.tier_configuration().tier_configuration_account('id')
        from_request['tier_config_id'] = request.tier_configuration().tier_configuration_id()

    return ExtensionLoggerAdapter(
        logger.logger,
        {
            **logger.extra,
            **{k: v for k, v in from_request.items() if v is not None},
        },
    )
