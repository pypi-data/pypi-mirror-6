import numpy as np
from numpy.testing import assert_array_equal
from nose.tools import assert_is

from landlab import RasterModelGrid


def test_flux_from_south_to_north():
    rmg = RasterModelGrid(4, 5)
    active_link_flux = np.array([0., 0., 0., 1., 1., 1., 3., 3., 3.,
                                 0., 0., 0., 0., 0., 0., 0., 0.])
    divs = rmg.calculate_flux_divergence_at_nodes(active_link_flux)

    assert_array_equal(
        divs,
        np.array([0.,  0.,  0.,  0., 0.,
                  0.,  1.,  1.,  1., 0.,
                  0.,  2.,  2.,  2., 0.,
                  0., -3., -3., -3., 0.]))
    
def test_flux_from_east_to_west():
    rmg = RasterModelGrid(4, 5)
    active_link_flux = np.array([0., 0., 0., 0., 0., 0., 0., 0., 0.,
                                 0., 1., 3., 6., 0., 1., 3., 6.])
    divs = rmg.calculate_flux_divergence_at_nodes(active_link_flux)

    assert_array_equal(
        divs,
        np.array([0., 0., 0., 0.,  0.,
                  0., 1., 2., 3., -6.,
                  0., 1., 2., 3., -6.,
                  0., 0., 0., 0.,  0.]))
    
def test_out_array():
    rmg = RasterModelGrid(4, 5)
    active_link_flux = np.array([0., 0., 0., 0., 0., 0., 0., 0., 0.,
                                 0., 1., 3., 6., 0., 1., 3., 6.])

    divs = np.empty(20)
    rtn_divs = rmg.calculate_flux_divergence_at_nodes(active_link_flux,
                                                      out=divs)

    assert_array_equal(
        divs,
        np.array([0., 0., 0., 0.,  0.,
                  0., 1., 2., 3., -6.,
                  0., 1., 2., 3., -6.,
                  0., 0., 0., 0.,  0.]))
    assert_is(rtn_divs, divs)
