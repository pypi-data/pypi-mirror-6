import numpy as np
from numpy.testing import assert_array_equal
from nose import with_setup
from nose.tools import assert_is, assert_equal, raises

from landlab.grid import raster_funcs as rfuncs


def setup_grid():
    from landlab import RasterModelGrid
    globals().update({
        'rmg': RasterModelGrid(4, 5),
        'values_at_nodes':  np.arange(20.),
    })


@with_setup(setup_grid)
def test_corner_with_scalar_cell_id():
    node_ids = rfuncs.node_id_of_cell_corner(rmg, np.array([0]), 0)
    assert_array_equal(node_ids, np.array([2]))


@with_setup(setup_grid)
def test_face_with_scalar_cell_id():
    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, np.array([0]), 0)
    assert_array_equal(node_ids, np.array([1]))


@with_setup(setup_grid)
def test_corner_with_iterable_cell_id():
    node_ids = rfuncs.node_id_of_cell_corner(rmg, np.array([0]), (5, ))
    assert_array_equal(node_ids, np.array([9]))


@with_setup(setup_grid)
def test_face_with_iterable_cell_id():
    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, np.array([0]), (5, ))
    assert_array_equal(node_ids, np.array([8]))


@with_setup(setup_grid)
def test_corner_with_no_cell_id():
    node_ids = rfuncs.node_id_of_cell_corner(rmg, np.array([0]))
    assert_array_equal(node_ids, np.array([2, 3, 4, 7, 8, 9]))


@with_setup(setup_grid)
def test_face_with_no_cell_id():
    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, np.array([0]))
    assert_array_equal(node_ids, np.array([1, 2, 3, 6, 7, 8]))


@with_setup(setup_grid)
def test_corner_multiple_corners():
    node_ids = rfuncs.node_id_of_cell_corner(rmg, np.array([0, 1]), (4, ))
    assert_array_equal(node_ids, np.array([8, 6]))


@with_setup(setup_grid)
def test_face_multiple_faces():
    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, np.array([0, 1]), (4, ))
    assert_array_equal(node_ids, np.array([7, 11]))


@with_setup(setup_grid)
def test_corner_multiple_corners_and_cells():
    node_ids = rfuncs.node_id_of_cell_corner(rmg, np.array([0, 1]), (4, 5))
    assert_array_equal(node_ids, np.array([8, 7]))


@with_setup(setup_grid)
def test_face_multiple_corners_and_cells():
    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, np.array([0, 1]), (4, 5))
    assert_array_equal(node_ids, np.array([7, 12]))


@with_setup(setup_grid)
def test_corner_type_tuple():
    node_ids = rfuncs.node_id_of_cell_corner(rmg, (0, 1), (4, 5))
    assert_array_equal(node_ids, np.array([8, 7]))


@with_setup(setup_grid)
def test_face_type_tuple():
    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, (0, 1), (4, 5))
    assert_array_equal(node_ids, np.array([7, 12]))


@with_setup(setup_grid)
def test_corner_type_list():
    node_ids = rfuncs.node_id_of_cell_corner(rmg, [0, 1], (4, 5))
    assert_array_equal(node_ids, np.array([8, 7]))


@with_setup(setup_grid)
def test_face_type_list():
    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, [0, 1], (4, 5))
    assert_array_equal(node_ids, np.array([7, 12]))


@with_setup(setup_grid)
def test_corner_type_scalar():
    node_ids = rfuncs.node_id_of_cell_corner(rmg, 2, (4, ))
    assert_array_equal(node_ids, np.array([16]))

    node_ids = rfuncs.node_id_of_cell_corner(rmg, 2, (4, 5))
    assert_array_equal(node_ids, np.array([16, 17]))

    node_ids = rfuncs.node_id_of_cell_corner(rmg, 1)
    assert_array_equal(node_ids, np.array([0, 1, 2, 5, 6, 7]))


@with_setup(setup_grid)
def test_face_type_scalar():
    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, 2, (4, ))
    assert_array_equal(node_ids, np.array([17]))

    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, 2, (4, 5))
    assert_array_equal(node_ids, np.array([17, 18]))

    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, 1)
    assert_array_equal(node_ids, np.array([5, 6, 7, 10, 11, 12]))


@raises(ValueError)
@with_setup(setup_grid)
def test_corner_length_mismatch():
    node_ids = rfuncs.node_id_of_cell_corner(rmg, (2, 3), (2, 4, 5))


@raises(ValueError)
@with_setup(setup_grid)
def test_face_length_mismatch():
    node_ids = rfuncs.node_id_of_cell_neighbor(rmg, (2, 3), (2, 4, 5))
