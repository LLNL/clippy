import pytest
import sys

sys.path.append('src')

from json_logic import jsonLogic
from typing import Any
import clippy.jsonlogic as jl
from clippy.jsonlogic.errors import JsonLogicArgumentError
from dataclasses import dataclass


@dataclass
class TV(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, val):
        return self.get(val)[1]

    def getname(self, val):
        return self.get(val)[0]


@pytest.fixture
def _i():
    return TV({n: (f'var{n}', jl.Variable(f'var{n}')) for n in range(1, 5)})


@pytest.fixture
def _f():
    fs = [1.1, 2.0, 2.1, 2.2, 3.3, 4.4]
    return TV({n: (f'var{int(n*10)}', jl.Variable(f'var{int(n*10)}')) for n in fs})


@pytest.fixture
def _s():
    ss = ['a', 'b', 'c', 'd', 'e']
    return TV({n: (f'var{n}', jl.Variable(f'var{n}')) for n in ss})


def assert_op(e: jl.Expression, d):
    assert jsonLogic(e.prepare(), d)


def test_lt_gt_ne(_s, _i, _f):
    test_int = [
        _i[1] < _i[2],
        _i[1] <= _i[1],
        _i[1] <= _i[2],
        _i[2] > _i[1],
        _i[2] >= _i[1],
        _i[2] >= _i[2],
        _i[1] != _i[2],
    ]
    test_float = [
        _f[1.1] < _f[2.0],
        _f[2.0] <= _f[2.0],
        _f[2.0] <= _f[2.1],
        _f[4.4] >= _f[2.1],
        _f[4.4] != _f[2.2],
    ]
    test_str = {
        _s['a'] < _s['b'],
        _s['a'] <= _s['a'],
        _s['b'] > _s['a'],
        _s['b'] >= _s['b'],
        _s['a'] != _s['b'],
    }

    for t in test_int:
        d = {_i.getname(k): k for k in _i}
        assert len(d) > 0
        assert_op(t, d)

    for t in test_float:
        d = {_f.getname(k): k for k in _f}
        assert_op(t, d)

    for t in test_str:
        d = {_s.getname(k): k for k in _s}
        assert_op(t, d)


def test_eq_add_mul_truediv_floordiv(_i, _f):
    test_int = [
        _i[1] + 1 == _i[2],
        _i[2] + 2 == _i[4],
        _i[2] + _i[2] == _i[4],
        _i[2] * 2 == _i[4],
        _i[2] * _i[2] == _i[4],
    ]
    test_float = [
        _f[1.1] + 1.1 == _f[2.2],
        _f[2.2] + 2.2 == _f[4.4],
        _f[2.2] + _f[2.2] == _f[4.4],
        _f[2.2] * 2 == _f[4.4],
        _f[2.2] * _f[2.0] == _f[4.4],
    ]

    for t in test_int:
        d = {_i.getname(k): k for k in _i}
        assert_op(t, d)

    for t in test_float:
        d = {_f.getname(k): k for k in _f}
        assert_op(t, d)


def test_bad_args():
    with pytest.raises(JsonLogicArgumentError):
        o = jl.Operation('foo', 1)
        v = jl.Variable('var1')
        jl.Expression(o, v, 1)


def test_operations():
    o = jl.Operation("foo", 1)
    assert repr(o) == "foo"
    assert str(o) == "foo"


# def test_float_eq_add_mul_truediv_floordiv(var1, var2, var4, var5, data_float):
#     for t in tests:
#         assert_op(t, data_float)
