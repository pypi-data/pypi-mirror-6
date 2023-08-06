import numpy as np
from numpy.testing import assert_array_equal

from landlab import RasterModelGrid


def test_inactive_boundaries():
    rmg = RasterModelGrid(3, 4, 1.)
    assert_array_equal(rmg.active_links,
                       np.array([ 1,  2,  5,  6, 11, 12, 13]))
    assert_array_equal(
        rmg.node_active_inlink_matrix,
        np.array([[-1, -1, -1, -1, -1,  0,  1, -1, -1,  2,  3, -1],
                  [-1, -1, -1, -1, -1,  4,  5,  6, -1, -1, -1, -1]]))

    rmg.set_inactive_boundaries(True, True, True, True)
    assert_array_equal(rmg.active_links, np.array([12]))
    assert_array_equal(
        rmg.node_active_inlink_matrix,
        np.array([[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1]]))
    assert_array_equal(
        rmg.node_active_outlink_matrix,
        np.array([[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1]]))
    assert_array_equal(
        rmg.active_node_links(),
        np.array([[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1]]))


def test_inactive_interiors():
    rmg = RasterModelGrid(4, 5, 1.)
    rmg.set_inactive_nodes([6, 12])
    assert_array_equal(rmg.active_node_links(),
                       np.array([[-1, -1, -1, -1, -1,
                                  -1, -1,  0,  1, -1,
                                  -1, -1, -1,  2, -1,
                                  -1,  3, -1,  4, -1],
                                 [-1, -1, -1, -1, -1,
                                  -1, -1, -1,  5,  6,
                                  -1,  7, -1, -1,  8,
                                  -1, -1, -1, -1, -1],
                                 [-1, -1,  0,  1, -1,
                                  -1, -1, -1,  2, -1,
                                  -1,  3, -1,  4, -1,
                                  -1, -1, -1, -1, -1],
                                 [-1, -1, -1, -1, -1,
                                  -1, -1,  5,  6, -1,
                                   7, -1, -1,  8, -1,
                                  -1, -1, -1, -1, -1]]))
