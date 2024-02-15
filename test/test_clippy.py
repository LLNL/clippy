import sys

sys.path.append('src')

import pytest
from clippy import Clippy
from clippy.error import ClippyValidationError


@pytest.fixture(scope="session")
def backend(pytestconfig):
    return pytestconfig.getoption("backend")


@pytest.fixture(scope='session')
def c(backend):
    return Clippy({'test': backend}, cmd_prefix='', loglevel=0)


def test_print_backend(backend):
    print(f"\ncommand line param (backend): {backend}")


def test_clippy_creation(c):
    assert 'returns_int' in c.test.__dict__


def test_clippy_call_with_string(c):
    assert c.test.call_with_string('Seth') == 'Howdy, Seth'
    with pytest.raises(ClippyValidationError) as e:
        c.test.call_with_string()


def test_clippy_returns_int(c):
    assert c.test.returns_int() == 42


def test_clippy_returns_string(c):
    assert c.test.returns_string() == 'asdf'


def test_clippy_returns_bool(c):
    assert c.test.returns_bool()


# def test_clippy_returns_dict(c):
#     d = c.test.returns_dict()
#     assert len(d) == 3
#     assert d.get('a') == 1
#     assert d.get('b') == 2
#     assert d.get('c') == 3


def test_clippy_returns_vec_int(c):
    assert c.test.returns_vec_int() == [0, 1, 2, 3, 4, 5]
