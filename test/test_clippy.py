import pytest
import sys

sys.path.append('src')

import clippy.jsonlogic as jl
import clippy
from clippy.error import ClippyValidationError, ClippyInvalidSelectorError

import logging

clippy.logger.setLevel(logging.WARN)
logging.getLogger().setLevel(logging.WARN)


@pytest.fixture()
def testbag():
    return clippy.TestBag()


@pytest.fixture()
def testset():
    return clippy.TestSet()


@pytest.fixture()
def testfun():
    return clippy.TestFunctions()


@pytest.fixture()
def testsel():
    return clippy.TestSelector()


def test_imports():
    assert "TestBag" in clippy.__dict__


def test_bag(testbag):

    testbag.insert(41)
    assert testbag.size() == 1
    testbag.insert(42)
    assert testbag.size() == 2
    testbag.insert(41)
    assert testbag.size() == 3
    testbag.remove(41)
    assert testbag.size() == 2
    testbag.remove(99)
    assert testbag.size() == 2


def test_clippy_call_with_string(testfun):
    assert testfun.call_with_string('Seth') == 'Howdy, Seth'
    with pytest.raises(ClippyValidationError):
        testfun.call_with_string()


def test_clippy_returns_int(testfun):
    assert testfun.returns_int() == 42


def test_clippy_returns_string(testfun):
    assert testfun.returns_string() == 'asdf'


def test_clippy_returns_bool(testfun):
    assert testfun.returns_bool()


def test_clippy_returns_dict(testfun):
    d = testfun.returns_dict()
    assert len(d) == 3
    assert d.get('a') == 1
    assert d.get('b') == 2
    assert d.get('c') == 3


def test_clippy_returns_vec_int(testfun):
    assert testfun.returns_vec_int() == [0, 1, 2, 3, 4, 5]


def test_clippy_returns_optional_string(testfun):
    assert testfun.call_with_optional_string() == 'Howdy, World'
    assert testfun.call_with_optional_string(name='Seth') == 'Howdy, Seth'


def test_selectors(testsel):
    assert hasattr(testsel, 'nodes')

    testsel.add(testsel.nodes, 'b', desc='docstring for nodes.b').add(
        testsel.nodes.b, 'c', desc='docstring for nodes.b.c'
    )
    assert hasattr(testsel.nodes, 'b')
    assert hasattr(testsel.nodes.b, 'c')
    assert testsel.nodes.b.__doc__ == 'docstring for nodes.b'
    assert testsel.nodes.b.c.__doc__ == 'docstring for nodes.b.c'

    assert isinstance(testsel.nodes.b, jl.Variable)
    assert isinstance(testsel.nodes.b.c, jl.Variable)

    with pytest.raises(ClippyInvalidSelectorError):
        testsel.add(testsel.nodes, '_bad', desc="this is a bad selector name")

    # with pytest.raises(ClippyInvalidSelectorError):
    #     testsel.add(testsel, 'bad', desc="this is a top-level selector")
