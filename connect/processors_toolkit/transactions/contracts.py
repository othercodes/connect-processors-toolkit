#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from abc import ABC, abstractmethod

from connect.eaas.core.responses import ProcessingResponse


class TransactionStatement(ABC):
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
    def execute(self, request: dict) -> ProcessingResponse:
        """
        Transaction main code, contains the domain logic.

        :param request: dict The Connect Request dictionary.
        :return: ProcessingResponse
        """

    @abstractmethod
    def compensate(self, request: dict, e: Exception) -> ProcessingResponse:
        """
        Compensate the transaction execution on fail.

        :param request: dict The Connect Request dictionary.
        :param e: Exception The occurred error/exception.
        :return: ProcessingResponse
        """
