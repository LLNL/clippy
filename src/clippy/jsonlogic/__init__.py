""" JSONLogic emitters """

from __future__ import annotations
from typing import Any
import json
from .operations import Operation, jl_operations
from .errors import JsonLogicArgumentError
from .classes import Entity
from .jsontypes import PyJsonType, deduce_type


class Operand(Entity):
    """An abstract base class representing an JSONLogic operand"""

    def __new__(cls, *_, **__):
        for dunder, op in jl_operations.items():
            setattr(cls, dunder, lambda self, *x, o=op: Expression(o, self, *x))
        return super().__new__(cls)

    def prepare(self) -> Any:
        """prepares the structure for json by converting it into something that can be dumped"""
        raise NotImplementedError()

    def to_json(self) -> str:
        """represents the object as JSON"""
        return json.dumps(self.prepare())

    def __str__(self):
        return self.to_json()


class Literal(Operand):
    """A JSONLogic literal."""

    def __init__(self, val: PyJsonType | Literal, docstr: str | None = None):
        super().__init__()
        self._rawval: PyJsonType = val._rawval if isinstance(val, Literal) else val

        self.type = deduce_type(val)
        if docstr is not None:
            self.__doc__ = docstr

    def __repr__(self):
        return str(self.type)

    def __str__(self):
        return str(self.type)

    def prepare(self) -> PyJsonType:
        return self.type.prepare()


class Variable(Operand):
    """A JSONLogic variable"""

    def __init__(self, var: str, docstr: str | None = None):
        super().__init__()
        self.var = var
        if docstr is not None:
            self.__doc__ = docstr

    def prepare(self):
        return {"var": self.var}


class Expression(Operand):
    """A JSONLogic expression"""

    def __init__(
        self,
        op: Operation,
        o1: Variable | Expression,
        *on: Operand | PyJsonType,
    ):
        super().__init__()
        # if op is None then this expression is just a native Selector held in o1.
        self.op = op
        self.o1 = o1
        if op.arity is not None and len(on) != op.arity - 1:
            raise JsonLogicArgumentError(
                f"incorrect number of arguments for {op}: wanted {op.arity}, got {len(on) + 1}"
            )
        # add the remaining variables, casting them to Literals if they're not Variables, Expressions, or Literals.
        self.on = tuple(Literal(o) if not isinstance(o, Operand) else o for o in on)

    def prepare(self):
        return {str(self.op): [self.o1.prepare()] + list(x.prepare() if isinstance(x, Operand) else x for x in self.on)}


# class Type(ABC):
#     """The abstract base class for all JSONLogic Types"""

# def __init__(self, value):
#     _value = value


# class Number(Type, float):
#     """Type representing a JSONLogic number"""


# class String(Type, str):
#     """Type representing a JSONLogic string"""


# class Object(Type, dict):
#     """Type representing a JSONLogic object (map)"""


# class Bool(Type):
#     """Type representing a JSONLogic boolean"""

#     def __init__(self, value):
#         self.


# class Array(Type, list):
#     """Type representing a JSONLogic array (list)"""


# class Null(Type, NoneType):
#     """Type representing a JSONLogic null"""


# class _Any(Type, Any):
#     """Type representing any JSONLogic type"""
