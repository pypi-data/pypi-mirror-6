import numpy as np
from numpy.testing import assert_array_equal
from nose import with_setup
from nose.tools import assert_is

from landlab import RasterModelGrid


_GRIDS = {}

def setup_grids():
    _GRIDS.update({
        'unit': RasterModelGrid(4, 5),
        'non_unit': RasterModelGrid(4, 5, 2.),
    })


@with_setup(setup_grids)
def test_unit_spacing():
    rmg, values_at_nodes = _GRIDS['unit'], np.arange(20)
    grads = rmg.calculate_gradients_at_active_links(values_at_nodes)

    assert_array_equal(grads, np.array([5, 5, 5, 5, 5, 5, 5, 5, 5,
                                        1, 1, 1, 1, 1, 1, 1, 1]))

    diffs = rmg.calculate_diff_at_active_links(values_at_nodes)
    assert_array_equal(grads, diffs)
    
    
@with_setup(setup_grids)
def test_non_unit_spacing():
    rmg, values_at_nodes = _GRIDS['non_unit'], np.arange(20)

    grads = rmg.calculate_gradients_at_active_links(values_at_nodes)
    assert_array_equal(grads, (1. / rmg.node_spacing) *
                       np.array([5, 5, 5, 5, 5, 5, 5, 5, 5,
                                 1, 1, 1, 1, 1, 1, 1, 1]))
    diffs = rmg.calculate_diff_at_active_links(values_at_nodes)
    assert_array_equal(grads, (1. / rmg.node_spacing) * diffs)


@with_setup(setup_grids)
def test_out_array():
    rmg, values_at_nodes = _GRIDS['non_unit'], np.arange(20)

    output_array = np.empty(17)
    rtn_array = rmg.calculate_gradients_at_active_links(values_at_nodes,
                                                        out=output_array)
    assert_array_equal(rtn_array, np.array([5, 5, 5, 5, 5, 5, 5, 5, 5,
                                            1, 1, 1, 1, 1, 1, 1, 1]) / rmg.node_spacing)
    assert_is(rtn_array, output_array)
    
    
@with_setup(setup_grids)
def test_diff_out_array():
    rmg = RasterModelGrid(4, 5)
    values = np.arange(20)
    diff = np.empty(17)
    rtn_diff = rmg.calculate_diff_at_active_links(values, out=diff)
    assert_array_equal(
        diff,
        np.array([5, 5, 5, 5, 5, 5, 5, 5, 5,
                  1, 1, 1, 1, 1, 1, 1, 1]))
    assert_is(rtn_diff, diff)
