#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from abc import ABC, abstractmethod
from typing import Callable, Optional, Tuple, Union

from connect.eaas.core.responses import (
    CustomEventResponse,
    ProcessingResponse,
    ProductActionResponse,
    ScheduledExecutionResponse,
    ValidationResponse,
)


class ProcessingTransaction(ABC):
    @abstractmethod
    def execute(self, request: dict) -> ProcessingResponse:
        """
        Transaction main code, contains the domain logic.

        :param request: dict The Connect Request dictionary.
        :return: ProcessingResponse
        """


class ProcessingTransactionStatement(ProcessingTransaction, ABC):  # pragma: no cover
    @abstractmethod
    def name(self) -> str:
        """
        Provides the transaction name.

        :return: str
        """

    @abstractmethod
    def should_execute(self, request: dict) -> bool:
        """
        True if the transaction needs to be executed, false otherwise.

        :param request: dict The Connect Request dictionary.
        :return: bool
        """

    @abstractmethod
    def compensate(self, request: dict, e: Exception) -> ProcessingResponse:
        """
        Compensate the transaction execution on fail.

        :param request: dict The Connect Request dictionary.
        :param e: Exception The occurred error/exception.
        :return: ProcessingResponse
        """


FnProcessingPredicate = Callable[[dict], bool]
FnProcessingTransaction = Callable[[dict], ProcessingResponse]
FnProcessingCompensation = Optional[Callable[[dict, Exception], ProcessingResponse]]

FnProcessingTransactionStatement = Tuple[str, FnProcessingPredicate, FnProcessingTransaction, FnProcessingCompensation]
AnyProcessingTransactionStatement = Union[ProcessingTransactionStatement, FnProcessingTransactionStatement]

Middleware = Callable[[dict, Optional[FnProcessingTransaction]], ProcessingResponse]


class ValidationTransaction(ABC):  # pragma: no cover
    @abstractmethod
    def validate(self, request: dict) -> ValidationResponse:
        """
        Validates the incoming request.

        :param request: The incoming Connect Request dictionary.
        :return: ValidationResponse
        """


FnValidationTransaction = Callable[[dict], ValidationResponse]
AnyValidationTransaction = Union[ValidationTransaction, FnValidationTransaction]


class ProductActionTransaction(ABC):  # pragma: no cover
    @abstractmethod
    def handle(self, request: dict) -> ProductActionResponse:
        """
        Handle the incoming action.

        :param request: The incoming request dictionary.
        :return: ProductActionResponse
        """


FnProductActionTransaction = Callable[[dict], ProductActionResponse]
AnyProductActionTransaction = Union[ProductActionTransaction, FnProductActionTransaction]


class CustomEventTransaction(ABC):  # pragma: no cover
    @abstractmethod
    def handle(self, request: dict) -> CustomEventResponse:
        """
        Handle the incoming event.

        :param request: The incoming request dictionary.
        :return: CustomEventResponse
        """


FnCustomEventTransaction = Callable[[dict], CustomEventResponse]
AnyCustomEventTransaction = Union[CustomEventTransaction, FnCustomEventTransaction]


class ScheduledTransaction(ABC):  # pragma: no cover
    @abstractmethod
    def handle(self, request: dict) -> ScheduledExecutionResponse:
        """
        Handle the incoming scheduled task.

        :param request: The incoming scheduled task dictionary.
        :return: ScheduledExecutionResponse
        """


FnScheduledTransaction = Callable[[dict], ScheduledExecutionResponse]
AnyScheduledTransaction = Union[ScheduledTransaction, FnScheduledTransaction]
