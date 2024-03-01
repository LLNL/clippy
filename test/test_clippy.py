import pytest
import sys

sys.path.append('src')

from clippy.error import ClippyValidationError
import clippy


@pytest.fixture(scope='session')
def bag():
    return clippy.TestBag()


@pytest.fixture(scope='session')
def set():
    return clippy.TestSet()


@pytest.fixture(scope='session')
def fun():
    return clippy.TestFunctions()


def test_imports():
    assert "TestBag" in clippy.__dict__


def test_bag(bag):

    bag.insert(41)
    assert bag.size() == 1
    bag.insert(42)
    assert bag.size() == 2
    bag.insert(41)
    assert bag.size() == 3
    bag.remove(41)
    assert bag.size() == 2
    bag.remove(99)
    assert bag.size() == 2
    bag.insert(50)
    bag.insert(51)
    assert bag.size() == 4
    bag.remove_if(bag.value > 49)
    assert bag.size() == 2
    bag.remove_if(bag.value > 49)
    assert bag.size() == 2
    assert "41" in str(bag) and "42" in str(bag)

    bag.insert(50)
    bag.insert(51)
    bag.remove_if(bag.value < 50)
    assert bag.size() == 2
    assert "50" in str(bag) and "51" in str(bag)

    bag.remove_if(bag.value == 51)
    assert bag.size() == 1
    assert "50" in str(bag)

    bag.remove_if(bag.value == 51)
    assert bag.size() == 1
    assert "50" in str(bag)


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


def test_clippy_returns_dict(fun):
    d = fun.returns_dict()
    assert len(d) == 3
    assert d.get('a') == 1
    assert d.get('b') == 2
    assert d.get('c') == 3


def test_clippy_returns_vec_int(fun):
    assert fun.returns_vec_int() == [0, 1, 2, 3, 4, 5]


def test_clippy_returns_optional_string(fun):
    assert fun.call_with_optional_string() == 'Howdy, World'
    assert fun.call_with_optional_string(name='Seth') == 'Howdy, Seth'
