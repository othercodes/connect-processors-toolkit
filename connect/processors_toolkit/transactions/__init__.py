#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from typing import Callable, List, Optional, Tuple, Union

from connect.eaas.core.responses import ProcessingResponse
from connect.processors_toolkit.transactions.contracts import TransactionStatement
from connect.processors_toolkit.transactions.exceptions import TransactionStatementException

FnPredicate = Callable[[dict], bool]
FnTransaction = Callable[[dict], ProcessingResponse]
FnCompensation = Optional[Callable[[dict, Exception], ProcessingResponse]]
FnTransactionStatement = Tuple[str, FnPredicate, FnTransaction, FnCompensation]
AnyTransactionStatement = Union[TransactionStatement, FnTransactionStatement]


class TupleTransactionStatement(TransactionStatement):
    def __init__(
            self,
            name: str,
            predicate: FnPredicate,
            transaction: FnTransaction,
            compensation: FnCompensation = None,
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


def select(transactions: List[AnyTransactionStatement], request: dict) -> TransactionStatement:
    """
    Select the correct transaction for the given request (context).

    :param transactions: List[AnyTransactionStatement] List of transactions.
    :param request: dict The Connect Request dictionary.
    :return: TransactionStatement
    """

    def __prepare_transaction_statement(statement_: AnyTransactionStatement) -> TransactionStatement:
        if isinstance(statement_, TransactionStatement):
            return statement_
        elif isinstance(statement_, Tuple):
            return TupleTransactionStatement(*statement_)
        else:
            raise TransactionStatementException.invalid('Invalid transaction statement.')

    for statement in [__prepare_transaction_statement(t) for t in transactions if t]:
        if statement.should_execute(request):
            return statement
    raise TransactionStatementException.not_selected('Unable to select a transaction.')


class TransactionSelector:
    def __init__(self, transactions: List[AnyTransactionStatement]):
        self.__transactions = transactions

    def select(self, request: dict) -> TransactionStatement:
        return select(self.__transactions, request)
