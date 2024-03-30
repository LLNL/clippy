import pytest
import sys

sys.path.append('src')

from clippy.jsonlogic import Expression, Variable, Literal, Operand, Operation
from clippy.jsonlogic.classes import Entity
from dataclasses import dataclass


@pytest.fixture
def op1():
    return Operation("op1", 1)


@pytest.fixture
def op2():
    return Operation("op2", 2)


@pytest.fixture
def v1():
    return Variable("var1", "docstring for var1")


@pytest.fixture
def v2():
    return Variable("var2")


@pytest.fixture
def l1():
    return Literal(5, "docstring for literal")


@pytest.fixture
def l2():
    return Literal("stringliteral")


def test_expression(op1, op2, v1, v2, l1, l2):
    e = Expression(op1, v1)
    assert e.to_json() == str(e) == '{"op1": [{"var": "var1"}]}'

    e = Expression(op2, v1, v2)
    assert e.to_json() == str(e) == '{"op2": [{"var": "var1"}, {"var": "var2"}]}'

    e = Expression(op2, v1, l1)
    assert e.to_json() == str(e) == '{"op2": [{"var": "var1"}, 5]}'


def test_operations():
    o = Operation("foo", 1)
    assert repr(o) == "foo"
    assert str(o) == "foo"


def test_literals(l1, l2):
    assert repr(l1) == str(l1) == "[Number]5"
    assert repr(l2) == str(l2) == "[String]stringliteral"


def test_operand():
    o = Operand()
    with pytest.raises(NotImplementedError):
        o.prepare()
