from copy import deepcopy
from typing import List, Optional


def find_by_id(elements: List, element_id: str, default: Optional[dict] = None) -> dict:
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
    :param override: Override dictionary to be merge into base.
    :return dict: The new dictionary.
    """
    new_base = deepcopy(base)
    for key, value in override.items():
        if key in new_base:
            if isinstance(new_base[key], dict) and isinstance(value, dict):
                new_base[key] = merge(new_base[key], value)
            elif isinstance(new_base[key], list) and isinstance(value, list):
                new_base[key] = new_base[key] + value
            else:
                new_base[key] = value
        else:
            new_base[key] = value

    return new_base
