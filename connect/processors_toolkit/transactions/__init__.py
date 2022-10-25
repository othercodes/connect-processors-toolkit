#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from typing import Callable, List, Optional, Tuple, Union

from connect.eaas.core.responses import ProcessingResponse
from connect.processors_toolkit.transactions.contracts import ProcessTransactionStatement
from connect.processors_toolkit.transactions.exceptions import TransactionStatementException

FnProcessPredicate = Callable[[dict], bool]
FnProcessTransaction = Callable[[dict], ProcessingResponse]
FnProcessCompensation = Optional[Callable[[dict, Exception], ProcessingResponse]]
FnProcessTransactionStatement = Tuple[str, FnProcessPredicate, FnProcessTransaction, FnProcessCompensation]
AnyProcessTransactionStatement = Union[ProcessTransactionStatement, FnProcessTransactionStatement]


class TupleProcessTransactionStatement(ProcessTransactionStatement):
    def __init__(
            self,
            name: str,
            predicate: FnProcessPredicate,
            transaction: FnProcessTransaction,
            compensation: FnProcessCompensation = None,
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


def select(transactions: List[AnyProcessTransactionStatement], request: dict) -> ProcessTransactionStatement:
    """
    Select the correct transaction for the given request (context).

    :param transactions: List[AnyProcessTransactionStatement] List of transactions.
    :param request: dict The Connect Request dictionary.
    :return: ProcessTransactionStatement
    """

    def __prepare_transaction_statement(statement_: AnyProcessTransactionStatement) -> ProcessTransactionStatement:
        if isinstance(statement_, ProcessTransactionStatement):
            return statement_
        elif isinstance(statement_, Tuple):
            return TupleProcessTransactionStatement(*statement_)
        else:
            raise TransactionStatementException.invalid('Invalid transaction statement.')

    for statement in [__prepare_transaction_statement(t) for t in transactions if t]:
        if statement.should_execute(request):
            return statement
    raise TransactionStatementException.not_selected('Unable to select a transaction.')


class TransactionSelector:
    def __init__(self, transactions: List[AnyProcessTransactionStatement]):
        self.__transactions = transactions

    def select(self, request: dict) -> ProcessTransactionStatement:
        return select(self.__transactions, request)


Middleware = Callable[[dict, Optional[FnProcessTransaction]], ProcessingResponse]


class TransactionExecutorMiddleware:
    def __init__(self, transaction: ProcessTransactionStatement):
        self.transaction = transaction

    def __call__(self, request: dict, _: Optional[FnProcessTransaction] = None) -> ProcessingResponse:
        try:
            return self.transaction.execute(request)
        except Exception as e:
            return self.transaction.compensate(request, e)


def prepare(transaction: ProcessTransactionStatement, middlewares: List[Middleware]) -> FnProcessTransaction:
    """
    Prepare the given transaction by creating the middleware callstack.

    :param transaction: ProcessTransactionStatement the transaction to prepare.
    :param middlewares: List[Middleware] The list of middleware to wrap the transaction.
    :return: FnProcessTransaction
    """

    def __make_middleware_callstack(current_: Middleware, next_: Optional[Middleware] = None) -> FnProcessTransaction:
        def __middleware_callstack(request: dict):
            return current_(request, next_)

        return __middleware_callstack

    # push the last middleware (TransactionExecutorMiddleware) into the stack.
    middlewares.append(TransactionExecutorMiddleware(transaction))

    callstack = None
    for middleware in reversed(middlewares):
        current = middleware
        if callstack is not None:
            current = __make_middleware_callstack(current, callstack)
        callstack = current

    return callstack
