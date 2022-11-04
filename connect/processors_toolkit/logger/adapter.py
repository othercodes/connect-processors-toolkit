#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from copy import deepcopy
from logging import LoggerAdapter
from typing import Any, Dict, List, Tuple, Union

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


def mask(data: Union[Dict, List, Tuple, Any], to_mask: List[str]) -> Union[Dict, List, Tuple, Any]:
    """
    Mask the required values by key in a dictionary.

    :param data: The dictionary to mask.
    :param to_mask: The list of keys to be masked.
    :return: The masked dictionary (it's a copy of the original).
    """
    if isinstance(data, dict):
        data = deepcopy(data)
        for key in data.keys():
            if key in to_mask:
                data[key] = '*' * len(str(data[key]))
            else:
                data[key] = mask(data[key], to_mask)
        return data
    elif isinstance(data, (list, tuple)):
        return [mask(item, to_mask) for item in data]
    else:
        return data
