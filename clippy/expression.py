import json
from clippy.serialization import ClippySerializable

class Expression(ClippySerializable):
    def __init__(self, op, o1, o2):
        super().__init__()
        self.op = op
        self.o1 = o1
        self.o2 = o2

    def _express(self, op, o, **kwargs):
        return Expression(op, self, o )

    def __lt__(self, o):
        return self._express("<", o)
    def __le__(self, o):
        return self._express("<=", o)
    def __eq__(self, o):
        return self._express("==",o)
    def __ne__(self, o):
        return self._express("!=",o)
    def __gt__(self, o):
        return self._express(">",o)
    def __ge__(self, o):
        return self._express(">=",o)
    def __add__(self, o):
        return self._express("+",o)
    def __sub__(self, o):
        return self._express("-",o)
    def __mul__(self, o):
        return self._express("*",o)
    def __matmul__(self, o):
        return self._express("@",o)
    def __truediv__(self, o):
        return self._express("/",o)
    def __floordiv__(self, o):
        return self._express("//",o)
    def __mod__(self, o):
        return self._express("%",o)
    def __divmod__(self, o):
        return self._express("divmod",o)
    def __pow__(self, o, modulo=None):
        return self._express("**",o, module=module)
    def __lshift__(self, o):
        return self._express("<<",o)
    def __rshift__(self, o):
        return self._express(">>",o)
    def __and__(self, o):
        return self._express("and",o)
    def __xor__(self, o):
        return self._express("^",o)
    def __or__(self, o):
        return self._express("or",o)

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

    def _express(self, op, o, **kwargs):
        return Expression(op, {"var": self.name}, o )

class Selector:
    def __init__(self, parent, name):
        # not used at the moment but could be potentially used
        # to get parent state information that can inform the 
        # field/expression creation
        self.parent = parent 
        self.name = name

    def __getattr__(self, key):
        field = Field(f"{self.name}.{key}")
        return field
