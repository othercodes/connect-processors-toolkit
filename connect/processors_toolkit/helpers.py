#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from typing import Any, List, Tuple, Type


def validator(rules: List[Type], values: List[Any]) -> Tuple[List[Exception], List[Any]]:
    """
    Validates given values using the given rules.

    The list of rules must be a list of ValueObjects or a list of functions
    that raises an Exception on error and return None on success.

    def validate_name(name: str) -> None:
        if len(name) < 3:
            raise ValueError(f'Invalid name <{name}>.')

    error, valid = validator(
        [uuid.UUID, validate_name],
        ['5338d5e4-6f3e-45fe-8af5-e2d96213b3f0', 'Vincent'],
    )

    :param rules: List of types that will be used to validate the values.
    :param values: List of values to validated.
    :return: Tuple of a list of exceptions and a list of valid values.
    """
    errors = []
    valid = []
    for rule, value in list(zip(rules, values)):
        try:
            result = rule(value)
            valid.append(value if result is None else result)
        except Exception as ex:
            errors.append(ex)
    return errors, valid
