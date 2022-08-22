#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union

from connect.eaas.extension import (
    CustomEventResponse,
    ProcessingResponse,
    ProductActionResponse,
    ScheduledExecutionResponse,
    ValidationResponse,
)
from connect.processors_toolkit.requests import RequestBuilder


class ProcessingFlow(ABC):  # pragma: no cover
    @abstractmethod
    def process(self, request: Union[RequestBuilder, dict]) -> ProcessingResponse:
        """
        Process the incoming request.

        :param request: The incoming request dictionary or RequestBuilder.
        :return: ProcessingResponse
        """


class ValidationFlow(ABC):  # pragma: no cover
    @abstractmethod
    def validate(self, request: Union[RequestBuilder, dict]) -> ValidationResponse:
        """
        Validates the incoming request.

        :param request: The incoming request dictionary or RequestBuilder.
        :return: ValidationResponse
        """


class ProductActionFlow(ABC):  # pragma: no cover
    @abstractmethod
    def handle(self, request: dict) -> ProductActionResponse:
        """
        Handle the incoming action.

        :param request: The incoming request dictionary.
        :return: ProductActionResponse
        """


class CustomEventFlow(ABC):  # pragma: no cover
    @abstractmethod
    def handle(self, request: dict) -> CustomEventResponse:
        """
        Handle the incoming event.

        :param request: The incoming request dictionary.
        :return: CustomEventResponse
        """


class ScheduledFlow(ABC):  # pragma: no cover
    @abstractmethod
    def handle(self, request: dict) -> ScheduledExecutionResponse:
        """
        Handle the incoming scheduled task.

        :param request: The incoming scheduled task dictionary.
        :return: ScheduledExecutionResponse
        """
