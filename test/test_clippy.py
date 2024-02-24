import sys

sys.path.append('src')

import pytest
from clippy.error import ClippyValidationError
import clippy


@pytest.fixture(scope='session')
def bag():
    return clippy.ClippyBag()


@pytest.fixture(scope='session')
def fun():
    return clippy.ClippyFunctions()


def test_imports():
    assert "ClippyBag" in clippy.__dict__


def test_clippy_bag(bag):

    bag.insert("foo")
    assert bag.size() == 1
    bag.insert("bar")
    assert bag.size() == 2
    bag.insert("foo")
    assert bag.size() == 3
    bag.remove("foo")
    assert bag.size() == 2
    bag.remove("zzz")
    assert bag.size() == 2
    assert "foo" in repr(bag) and "bar" in repr(bag)
    assert "foo" in str(bag) and "bar" in str(bag)


def test_clippy_call_with_string(fun):
    assert fun.call_with_string('Seth') == 'Howdy, Seth'
    with pytest.raises(ClippyValidationError) as e:
        fun.call_with_string()


def test_clippy_returns_int(fun):
    assert fun.returns_int() == 42


def test_clippy_returns_string(fun):
    assert fun.returns_string() == 'asdf'


def test_clippy_returns_bool(fun):
    assert fun.returns_bool()


# def test_clippy_returns_dict(c):
#     d = c.test.returns_dict()
#     assert len(d) == 3
#     assert d.get('a') == 1
#     assert d.get('b') == 2
#     assert d.get('c') == 3


def test_clippy_returns_vec_int(fun):
    assert fun.returns_vec_int() == [0, 1, 2, 3, 4, 5]


def test_clippy_returns_optional_string(fun):
    assert fun.call_with_optional_string() == 'Howdy, World'
    assert fun.call_with_optional_string(name='Seth') == 'Howdy, Seth'
