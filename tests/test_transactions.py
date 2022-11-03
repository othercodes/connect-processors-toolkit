from typing import Optional

import pytest
from connect.eaas.core.responses import ProcessingResponse
from connect.processors_toolkit.requests import RequestBuilder
from connect.processors_toolkit.transactions import make_middleware_callstack, TransactionSelector, TransactionExecutorMiddleware
from connect.processors_toolkit.transactions.contracts import (
    FnProcessingTransaction,
    ProcessingTransactionStatement,
)
from connect.processors_toolkit.transactions.exceptions import (
    TransactionStatementNotSelected,
    InvalidTransactionStatement,
)


class CreateCustomer(ProcessingTransactionStatement):
    def name(self) -> str:
        return 'Create Customer'

    def should_execute(self, request: dict) -> bool:
        try:
            param = next(filter(lambda parameter: parameter['id'] == 'PARAM_CUSTOMER_ID', request['params']))
            return param.get('value', '') == ''
        except StopIteration:
            return True

    def execute(self, request: dict) -> ProcessingResponse:
        return ProcessingResponse.done()

    def compensate(self, request: dict, e: Exception) -> ProcessingResponse:
        return ProcessingResponse.done()


def should_create_subscription(request: dict) -> bool:
    try:
        param = next(filter(lambda parameter: parameter['id'] == 'PARAM_SUBS_ID', request['params']))
        return param.get('value', '') == ''
    except StopIteration:
        return True


def create_subscription(_: dict) -> ProcessingResponse:
    return ProcessingResponse.done()


def should_approve_request(request: dict) -> bool:
    return request.get('status', 'pending') != 'approved'


def approve_request(_: dict) -> ProcessingResponse:
    return ProcessingResponse.done()


def approve_request_compensate(_: dict) -> ProcessingResponse:
    return ProcessingResponse.done()


def mdl_one(request: dict, nxt: Optional[FnProcessingTransaction] = None) -> ProcessingResponse:
    print(f'001 Before')
    response = nxt(request)
    print(f'001 After')
    return response


def mdl_two(request: dict, nxt: Optional[FnProcessingTransaction] = None) -> ProcessingResponse:
    print(f'002 Before')
    response = nxt(request)
    print(f'002 After')
    return response


def test_transaction_selector_should_select_the_correct_statement():
    request = RequestBuilder() \
        .with_status('pending') \
        .with_param('PARAM_CUSTOMER_ID', 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e') \
        .with_param('PARAM_SUBS_ID', 'bc180aa9-4a41-4c5e-ad0d-656f1dc0c6d9') \
        .raw()

    ts = TransactionSelector([
        CreateCustomer(),
        ('Create Subscription', should_create_subscription, create_subscription),
        ('Approve Request', should_approve_request, approve_request, approve_request_compensate),
    ])

    transaction = ts.select(request)

    assert transaction.name() == 'Approve Request'
    assert transaction.should_execute(request) == True
    assert transaction.execute(request).status == 'success'

    with pytest.raises(Exception):
        transaction.compensate(request, Exception())


def test_transaction_selector_should_raise_exception_on_invalid_statement():
    request = RequestBuilder() \
        .with_status('pending') \
        .with_param('PARAM_CUSTOMER_ID', 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e') \
        .raw()

    ts = TransactionSelector([
        CreateCustomer,
    ])

    with pytest.raises(InvalidTransactionStatement):
        ts.select(request)


def test_transaction_selector_should_raise_exception_on_transaction_not_selected():
    request = RequestBuilder() \
        .with_status('pending') \
        .with_param('PARAM_CUSTOMER_ID', 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e') \
        .raw()

    ts = TransactionSelector([])

    with pytest.raises(TransactionStatementNotSelected):
        ts.select(request)


def tests_transaction_preparer_should_build_a_transaction_callstack_successfully():
    executor = TransactionExecutorMiddleware(CreateCustomer())
    transaction = make_middleware_callstack([
        mdl_one,
        mdl_two,
        executor
    ])

    response = transaction(
        RequestBuilder() \
            .with_status('pending') \
            .with_param('PARAM_CUSTOMER_ID', 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e') \
            .raw(),
    )

    assert response.status == 'success'
