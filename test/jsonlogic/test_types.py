import warnings
import sys
import pytest

sys.path.append('src')
from clippy.jsonlogic.jsontypes import (
    JsonArray,
    JsonBool,
    JsonNumber,
    JsonStr,
    JsonObj,
    deduce_type,
    PyJsonType,
    JsonType,
)


def test_bool():
    b = JsonBool(True)
    assert b.typename == 'Boolean'
    assert b.val is True
    assert isinstance(b.val, bool)
    assert str(b) == "[Boolean]True"
    assert b.prepare() is True


def test_int():
    b = JsonNumber(10)
    assert b.typename == 'Number'
    assert b.val == 10
    assert isinstance(b.val, int)
    assert str(b) == "[Number]10"
    assert b.prepare() == 10


def test_float():
    b = JsonNumber(10.1)
    assert b.typename == 'Number'
    assert b.val == 10.1
    assert isinstance(b.val, float)
    assert str(b) == "[Number]10.1"
    assert b.prepare() == 10.1


def test_dict():
    d = {'a': 1, 'b': 2}
    b = JsonObj(d)
    assert b.typename == 'Object'
    assert b.val == d
    assert isinstance(b.val, dict)
    assert str(b).startswith("[Object]")
    assert b.prepare() == d


def test_str():
    b = JsonStr("hello")
    assert b.typename == 'String'
    assert b.val == "hello"
    assert isinstance(b.val, str)
    assert str(b).startswith("[String]")
    assert b.prepare() == "hello"


def test_list():
    d = [1, 2, 3, 4, 5]
    b = JsonArray(d)
    assert b.typename == 'Array'
    assert b.val == d
    assert isinstance(b.val, list)
    assert str(b).startswith("[Array]")
    assert b.prepare() == d


def test_deduce():
    assert isinstance(deduce_type(True), JsonBool)
    assert isinstance(deduce_type(10), JsonNumber)
    assert isinstance(deduce_type(10.1), JsonNumber)
    assert isinstance(deduce_type({'a': 1}), JsonObj)
    assert isinstance(deduce_type(""), JsonStr)
    assert isinstance(deduce_type([]), JsonArray)

    with pytest.warns(UserWarning, match=r"cannot deduce type.*"):
        assert isinstance(deduce_type(complex(1, 2)), JsonStr)


def test_jsontype():
    class TestType(JsonType):
        pass

    tt = TestType(10)
    assert tt.typename == "UNDEFINED"
    assert str(tt) == "[UNDEFINED]10"
    with pytest.raises(NotImplementedError):
        tt.prepare()
