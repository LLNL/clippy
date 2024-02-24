# Copyright 2020 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT

""" Holds the expression building code. """

from .serialization import ClippySerializable


class Expression(ClippySerializable):
    def __init__(self, op, o1, o2):
        super().__init__()
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
        raise NotImplementedError("syntax a in b is not supported. Use b.contains(a) instead.")
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


class Field(Expression):
    def __init__(self, name):
        self.name = name

    # ~ def to_json(self):
    # ~ return f"{{\"var\": [\"{self.name}\"]}}"

    def to_serial(self):
        return {"var": self.name}

    def _express(self, op, o):
        return Expression(op, self, o)


class Selector:
    def __init__(self, parent, name):
        # not used at the moment but could be potentially used
        # to get parent state information that can inform the
        # field/expression creation
        self.parent = parent
        self._fld_name_sel_08 = name

    def __getattr__(self, key):
        field = Field(f"{self._fld_name_sel_08}.{key}")
        return field
