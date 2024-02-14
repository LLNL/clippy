import sys

sys.path.append('src')
import pytest
from clippy import Clippy


@pytest.fixture(scope="session")
def backend(pytestconfig):
    return pytestconfig.getoption("backend")


def test_print_backend(backend):
    print(f"\ncommand line param (backend): {backend}")


def test_clippy_creation(backend):
    c = Clippy({'test': backend}, cmd_prefix='', loglevel=0)
    print('past create!!!!')
    assert 'returns_int' in c.test.__dict__
