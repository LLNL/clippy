# pylint: disable=too-few-public-methods

""" JSON typing classes and functions """

from __future__ import annotations
from abc import ABC
import warnings

from typing import Any

PyJsonType = int | float | bool | str | list | dict


class JsonType(ABC):
    '''The abstract base class for JSON types'''

    typename = 'UNDEFINED'

    def __init__(self, val):
        self.val = val

    def __str__(self):
        return f'[{self.typename}]{self.val}'

    def prepare(self) -> PyJsonType:
        '''Prepares the type for JSON serialization'''
        raise NotImplementedError('class has not defined prepare()')


class JsonNumber(JsonType):
    '''A JSON Number type'''

    typename = 'Number'

    def prepare(self):
        return int(self.val) if isinstance(self.val, int) else float(self.val)


class JsonBool(JsonType):
    '''A JSON Boolean type'''

    typename = 'Boolean'

    def prepare(self) -> bool:
        return bool(self.val)


class JsonStr(JsonType):
    '''A JSON String type'''

    typename = 'String'

    def prepare(self) -> str:
        return str(self.val)


class JsonArray(JsonType):
    '''A JSON Array type'''

    typename = 'Array'

    def prepare(self) -> list:
        return list(self.val)


class JsonObj(JsonType):
    '''A JSON Object type'''

    typename = 'Object'

    def prepare(self) -> dict:
        return dict(self.val)


def deduce_type(val: Any) -> JsonType:
    """Given a value, try to deduce the json datatype. Default is string."""
    if isinstance(val, bool):
        return JsonBool(val)
    if isinstance(val, (float, int)):
        return JsonNumber(val)
    if isinstance(val, list):
        return JsonArray(val)
    if isinstance(val, dict):
        return JsonObj(val)
    if not isinstance(val, str):
        warnings.warn(f"cannot deduce type of {val} ({type(val)}); assuming string", UserWarning)
    return JsonStr(str(val))
