import numpy as np
from numpy.testing import assert_array_equal
from nose.tools import (with_setup, assert_tuple_equal, assert_true,
                        assert_false, )

from landlab import RasterModelGrid


def setup_grid():
    globals().update({
        'rmg': RasterModelGrid(4, 5)
    })


def test_boundary_node():
    rmg = RasterModelGrid(5, 6)
    assert_true(rmg.has_boundary_neighbor(0))
    assert_false(rmg.has_boundary_neighbor(14))


@with_setup(setup_grid)
def test_last_index():
    assert_true(rmg.has_boundary_neighbor(-1))


@with_setup(setup_grid)
def test_id_as_list():
    assert_array_equal(rmg.has_boundary_neighbor([-1, 0]),
                       np.array([True, True]))


@with_setup(setup_grid)
def test_id_as_array():
    assert_array_equal(rmg.has_boundary_neighbor(np.arange(20)),
                       np.array([True, True, True, True, True,
                                 True, True, True, True, True,
                                 True, True, True, True, True,
                                 True, True, True, True, True]))


def test_id_as_array_with_one_interior():
    rmg = RasterModelGrid(5, 5)
    assert_array_equal(rmg.has_boundary_neighbor(np.arange(25)),
                       np.array([True, True,  True, True, True,
                                 True, True,  True, True, True,
                                 True, True, False, True, True,
                                 True, True,  True, True, True,
                                 True, True,  True, True, True]))
