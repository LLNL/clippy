# Copyright 2020 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT

""" Holds the expression building code. """

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from .classes import Entity


@dataclass
class Operation(Entity):
    """A JSONLogic operation"""

    op: str
    arity: int | None  # None means unlimited

    def __repr__(self):
        return self.op

    def __str__(self):
        return str(self.op)


_jl_lt = Operation('<', 2)
_jl_le = Operation('<=', 2)
_jl_eq = Operation('==', 2)
_jl_ne = Operation('!=', 2)
_jl_gt = Operation('>', 2)
_jl_ge = Operation('>=', 2)
_jl_add = Operation('+', 2)
_jl_sub = Operation('-', 2)
_jl_mul = Operation('*', 2)
_jl_matmul = Operation('@', 2)
_jl_truediv = Operation('/', 2)
_jl_floordiv = Operation('//', 2)
_jl_mod = Operation('%', 2)
_jl_divmod = Operation('divmod', 2)
_jl_pow = Operation('**', 2)
_jl_lshift = Operation('<<', 2)
_jl_rshift = Operation('>>', 2)
_jl_and = Operation('and', None)
_jl_not = Operation('not', 1)
_jl_xor = Operation('^', 2)
_jl_or = Operation('or', 2)
# _jl_contains = Operation():
#     raise NotImplementedError("syntax a in b is not supported. Use b.contains(a) instead.")
#     # will not work when written as "x in set",
#     #   b/c the in-operator always converts the result to bool
#     #   https://stackoverflow.com/questions/38542543/functionality-of-python-in-vs-contains
#     #   https://bugs.python.org/issue16011
#     # return Expression("in", o, self)

# # to be modeled after Pandas' str.contains
_jl_contains = Operation('in', 2)
_jl_regex = Operation('regex', 2)

# string and array concatenation
_jl_cat = Operation('cat', None)

jl_operations: dict[str, Operation | Callable[..., Operation]] = {
    '__lt__': _jl_lt,
    '__le__': _jl_le,
    '__eq__': _jl_eq,
    '__ne__': _jl_ne,
    '__gt__': _jl_gt,
    '__ge__': _jl_ge,
    '__add__': _jl_add,
    '__sub__': _jl_sub,
    '__mul__': _jl_mul,
    '__matmul__': _jl_matmul,
    '__truediv__': _jl_truediv,
    '__floordiv__': _jl_floordiv,
    '__mod__': _jl_mod,
    '__divmod__': _jl_divmod,
    '__pow__': _jl_pow,
    '__lshift__': _jl_lshift,
    '__rshift__': _jl_rshift,
    '__and__': _jl_and,
    '__xor__': _jl_xor,
    '__or__': _jl_or,
    'contains': _jl_contains,
    'regex': _jl_regex,
    'cat': _jl_cat,
}
