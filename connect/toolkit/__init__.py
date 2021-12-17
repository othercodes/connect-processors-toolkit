from __future__ import annotations

from copy import deepcopy
from typing import Any, List, Optional, Union


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


def with_member(dictionary: dict, member_id: str, member: Any) -> dict:
    """
    Add a new member to the given dictionary.

    :param dictionary: The base dictionary.
    :param member_id: The member id.
    :param member: The member to be added.
    :return: The updated dictionary.
    """
    if dictionary.get(member_id) is None:
        if isinstance(member, dict):
            dictionary.update({member_id: {}})
        elif isinstance(member, list):
            dictionary.update({member_id: []})

    if isinstance(member, dict):
        dictionary.get(member_id, {}).update({k: v for k, v in member.items() if v is not None})
    elif isinstance(member, list):
        dictionary.get(member_id, []).extend(member)
    else:
        dictionary.update({member_id: member})

    return dictionary


def without_member(dictionary: dict, member_id: str) -> dict:
    dictionary.pop(member_id, None)
    return dictionary


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
                new_base[key] = new_base[key].extend(value)
            else:
                new_base[key] = value
        else:
            new_base[key] = value

    return new_base


def _param_members(param: dict, value: Optional[Union[str, dict]] = None, value_error: Optional[str] = None) -> dict:
    if isinstance(value, dict):
        key = 'structured_value'
        new_value = param.get(key, {})
        new_value.update(value)
    else:
        key = 'value'
        new_value = value

    return {key: new_value, 'value_error': value_error}


def make_tier(tier_type: str = 'customer') -> dict:
    return {
        "name": 'Acme LLC',
        "type": tier_type,
        "external_id": "100000",
        "external_uid": "00000000-0000-0000-0000-000000000000",
        "contact_info": {
            "address_line1": "222 Fake Street",
            "address_line2": "1B",
            "city": "City",
            "state": "State",
            "postal_code": "000000",
            "country": "US",
            "contact": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@fake.email.com",
                "phone_number": {
                    "country_code": "+1",
                    "area_code": "100",
                    "phone_number": "123456",
                    "extension": "001",
                },
            },
        },
    }
