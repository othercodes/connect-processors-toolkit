#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from typing import List, Optional, Tuple

from connect.eaas.core.responses import ProcessingResponse
from connect.processors_toolkit.transactions.contracts import (
    AnyProcessingTransactionStatement,
    FnProcessingCompensation,
    FnProcessingPredicate,
    FnProcessingTransaction,
    Middleware,
    ProcessingTransactionStatement,
)
from connect.processors_toolkit.transactions.exceptions import TransactionStatementException


class TupleProcessTransactionStatement(ProcessingTransactionStatement):
    def __init__(
            self,
            name: str,
            predicate: FnProcessingPredicate,
            transaction: FnProcessingTransaction,
            compensation: FnProcessingCompensation = None,
    ):
        self._name = name
        self._predicate = predicate
        self._transaction = transaction
        self._compensation = compensation

    def name(self) -> str:
        return self._name

    def should_execute(self, request: dict) -> bool:
        return self._predicate(request)

    def execute(self, request: dict) -> ProcessingResponse:
        return self._transaction(request)

    def compensate(self, request: dict, e: Exception) -> ProcessingResponse:
        if self._compensation is None:
            raise e
        return self._compensation(request, e)


def select(transactions: List[AnyProcessingTransactionStatement], request: dict) -> ProcessingTransactionStatement:
    """
    Select the correct transaction for the given request (context).

    :param transactions: List[AnyProcessingTransactionStatement] List of transactions.
    :param request: dict The Connect Request dictionary.
    :return: ProcessTransactionStatement
    """

    def __prepare_transaction_statement(statement: AnyProcessingTransactionStatement) -> ProcessingTransactionStatement:
        if isinstance(statement, ProcessingTransactionStatement):
            return statement
        elif isinstance(statement, Tuple):
            return TupleProcessTransactionStatement(*statement)
        else:
            raise TransactionStatementException.invalid('Invalid transaction statement.')

    for statement in [__prepare_transaction_statement(t) for t in transactions if t]:
        if statement.should_execute(request):
            return statement
    raise TransactionStatementException.not_selected('Unable to select a transaction.')


class TransactionSelector:
    def __init__(self, transactions: List[AnyProcessingTransactionStatement]):
        self.__transactions = transactions

    def select(self, request: dict) -> ProcessingTransactionStatement:
        return select(self.__transactions, request)


class TransactionExecutorMiddleware:
    def __init__(self, transaction: ProcessingTransactionStatement):
        self.transaction = transaction

    def __call__(self, request: dict, _: Optional[FnProcessingTransaction] = None) -> ProcessingResponse:
        try:
            return self.transaction.execute(request)
        except Exception as e:
            return self.transaction.compensate(request, e)


def make_middleware_callstack(middlewares: List[Middleware]) -> FnProcessingTransaction:
    """
    Makes the middleware callstack.

    :param middlewares: List[Middleware] The list of middlewares to prepare.
    :return: FnProcessingTransaction
    """

    def __make_middleware(current_: Middleware, next_: Optional[Middleware] = None) -> FnProcessingTransaction:
        def __middleware_callstack(request: dict):
            return current_(request, next_)

        return __middleware_callstack

    callstack = None
    for middleware in reversed(middlewares):
        current = middleware
        if callstack is not None:
            current = __make_middleware(current, callstack)
        callstack = current

    return callstack
