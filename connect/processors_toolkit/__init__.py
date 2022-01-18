from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple, Type, Union


def find_by_id(elements: List[dict], element_id: str, default: Optional[dict] = None) -> Optional[dict]:
    """
    Searches for a parameter/item with the given ``id`` within the ``list``.

    :param elements: The list of parameters/items to search.
    :param element_id: The id of the parameter/item to find.
    :param default: Default value to return if item is not found.
    :return: The parameter/list, or ``default`` if it was not found.
    """
    try:
        return next(filter(lambda element: element['id'] == element_id, elements))
    except StopIteration:
        return default


def merge(base: dict, override: dict) -> dict:
    """
    Merge two dictionaries (override into base) recursively.

    :param base: The base dictionary.
    :param override: Override dictionary to be merged into base.
    :return dict: The new dictionary.
    """
    new_base = deepcopy(base)
    for key, value in override.items():
        if key in new_base:
            if isinstance(new_base[key], dict) and isinstance(value, dict):
                new_base[key] = merge(new_base[key], value)
            elif isinstance(new_base[key], list) and isinstance(value, list):
                new_base[key].extend(value)
            else:
                new_base[key] = value
        else:
            new_base[key] = value

    return new_base


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
