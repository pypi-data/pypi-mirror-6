import numpy as np
from numpy.testing import assert_array_equal
from nose import with_setup
from nose.tools import assert_is

from landlab import RasterModelGrid


_GRID = None
_VALUES_AT_NODES = None


def setup_unit_grid():
    global _GRID, _VALUES_AT_NODES
    _GRID = RasterModelGrid(4, 5)
    _VALUES_AT_NODES = np.arange(20)


def setup_non_unit_grid():
    global _GRID, _VALUES_AT_NODES
    _GRID = RasterModelGrid(4, 5, 2.)
    _VALUES_AT_NODES = np.arange(20)


@with_setup(setup_unit_grid)
def test_unit_spacing():
    grads = _GRID.calculate_gradients_at_links(_VALUES_AT_NODES)
    assert_array_equal(
        grads,
        np.array([5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                 dtype=float))
    diffs = _GRID.calculate_diff_at_links(_VALUES_AT_NODES)
    assert_array_equal(grads, diffs)
    
    
@with_setup(setup_non_unit_grid)
def test_non_unit_spacing():
    grads = _GRID.calculate_gradients_at_links(_VALUES_AT_NODES)
    assert_array_equal(
        grads, np.array([5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        dtype=float) / _GRID.node_spacing)
    diffs = _GRID.calculate_diff_at_links(_VALUES_AT_NODES)
    assert_array_equal(grads, diffs / _GRID.node_spacing)


@with_setup(setup_unit_grid)
def test_out_array():
    grads = np.empty(31)
    rtn_grads = _GRID.calculate_gradients_at_links(_VALUES_AT_NODES, out=grads)
    assert_array_equal(
        grads,
        np.array([5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                 dtype=float))
    assert_is(rtn_grads, grads)


@with_setup(setup_unit_grid)
def test_diff_out_array():
    diff = np.empty(31)
    rtn_diff = _GRID.calculate_diff_at_links(_VALUES_AT_NODES, out=diff)
    assert_array_equal(
        diff,
        np.array([5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                 dtype=float))
    assert_is(rtn_diff, diff)
