#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations


class TransactionStatementException(Exception):
    @staticmethod
    def invalid(msg: str) -> InvalidTransactionStatement:
        return InvalidTransactionStatement(msg)

    @staticmethod
    def not_selected(msg: str) -> TransactionStatementNotSelected:
        return TransactionStatementNotSelected(msg)


class InvalidTransactionStatement(TransactionStatementException):
    pass


class TransactionStatementNotSelected(TransactionStatementException):
    pass
