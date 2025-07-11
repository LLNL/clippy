# Copyright 2020 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT

""" Holds the expression building code. """

from __future__ import annotations
import json
from typing import Any
from .backends.serialization import ClippySerializable
from . import constants
from .clippy_types import AnyDict


class Expression(ClippySerializable):
    '''A clippy expression is a triple of (operation, operand1, operand2) where
    operation is a string representing an operation (e.g., `"<"` for "less than")
    and operand1 is a Selector object. Operand2 may be a selector object, or any
    constant value. It can also be an expression.
    '''

    # Selectors are currently subclasses of Expression where both op and operand2 are None.
    # This should probably change.

    def __init__(self, op: str | None, o1: Selector, o2: Any):
        super().__init__()
        # if op is None then this expression is just a native Selector held in o1.
        self.op = op
        self.o1 = o1
        self.o2 = o2

    def _express(self, op, o):
        return Expression(op, self, o)

    def __lt__(self, o):
        return self._express("<", o)

    def __le__(self, o):
        return self._express("<=", o)

    def __eq__(self, o):
        return self._express("==", o)

    def __ne__(self, o):
        return self._express("!=", o)

    def __gt__(self, o):
        return self._express(">", o)

    def __ge__(self, o):
        return self._express(">=", o)

    def __add__(self, o):
        return self._express("+", o)

    def __sub__(self, o):
        return self._express("-", o)

    def __mul__(self, o):
        return self._express("*", o)

    def __matmul__(self, o):
        return self._express("@", o)

    def __truediv__(self, o):
        return self._express("/", o)

    def __floordiv__(self, o):
        return self._express("//", o)

    def __mod__(self, o):
        return self._express("%", o)

    def __divmod__(self, o):
        return self._express("divmod", o)

    def __pow__(self, o):
        return self._express("**", o)

    def __lshift__(self, o):
        return self._express("<<", o)

    def __rshift__(self, o):
        return self._express(">>", o)

    def __and__(self, o):
        return self._express("and", o)

    def __xor__(self, o):
        return self._express("^", o)

    def __or__(self, o):
        return self._express("or", o)

    def __contains__(self, o):
        raise NotImplementedError(
            "syntax a in b is not supported. Use b.contains(a) instead."
        )
        # will not work when written as "x in set",
        #   b/c the in-operator always converts the result to bool
        #   https://stackoverflow.com/questions/38542543/functionality-of-python-in-vs-contains
        #   https://bugs.python.org/issue16011
        # return Expression("in", o, self)

    # to be modeled after Pandas' str.contains
    def contains(self, o, regex=False):
        oper = "in" if not regex else "regex"
        return Expression(oper, o, self)

    #        return self._express(oper, o)

    # string and array concatenation
    def cat(self, o):
        return self._express("cat", o)

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.to_json()

    def to_json(self):
        o1 = self.o1
        o2 = self.o2
        return f"{{\"{self.op}\": [{o1},{o2}] }}"

    def to_serial(self):
        o1 = self.o1
        o2 = self.o2
        if hasattr(o1, "to_serial"):
            o1 = o1.to_serial()
        if hasattr(o2, "to_serial"):
            o2 = o2.to_serial()

        return {self.op: [o1, o2]}


class Selector(Expression):  # pylint: disable=abstract-method
    '''A Selector is a subset of `Expression` and represents a single variable.'''

    def __init__(self, parent: Selector | None, name: str, docstr: str):
        super().__init__(
            None, self, None
        )  # op and o2 are None to represent this as a variable.
        self.parent = parent
        self.name = name
        setattr(self, '__doc__', docstr)
        self.fullname: str = (
            self.name if self.parent is None else f"{self.parent.fullname}.{self.name}"
        )
        self.subselectors: set[Selector] = set()

    def __hash__(self):
        return hash(self.fullname)

    def to_dict(self):
        return {'var': self.fullname}

    def hierarchy(self, acc: list[tuple[str, str]] | None = None):
        if acc is None:
            acc = []
        acc.append((self.fullname, self.__doc__ or ''))
        for subsel in self.subselectors:
            subsel.hierarchy(acc)
        return acc

    def describe(self):
        hier = self.hierarchy()
        maxlen = max((len(sub_desc[0]) for sub_desc in hier))
        return '\n'.join(
            f'{sub_desc[0]:<{maxlen+2}} {sub_desc[1]}' for sub_desc in hier
        )

    def __str__(self):
        return repr(self.to_dict())

    def __repr__(self):
        return repr(self.to_dict())

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_serial(self):
        return {"var": self.fullname}

    def _express(self, op, o):
        return Expression(op, self, o)

    def _add_subselector(self, name: str, docstr: str):
        '''add a subselector to this selector'''
        subsel = Selector(self, name, docstr)
        setattr(self, name, subsel)
        self.subselectors.add(subsel)

    def _del_subselector(self, name: str):
        delattr(self, name)
        self.subselectors.remove(getattr(self, name))

    def _clear_subselectors(self):
        '''removes all subselectors'''
        for subsel in self.subselectors:
            delattr(self, subsel.name)
        self.subselectors = set()

    def _import_from_dict(self, d: AnyDict, merge: bool = False):
        '''Imports subselectors from a dictionary.
        If `merge = True`, do not clear subselectors first.
        '''

        # clear all children
        if not merge:
            self._clear_subselectors()

        for name, subdict in d.get(constants.SELECTOR_KEY, {}).items():
            docstr = subdict.get('__doc__', '')
            self._add_subselector(name, docstr)
            getattr(self, name)._import_from_dict(subdict)
