import numpy as np
from numpy.testing import assert_array_equal
from nose.tools import (assert_is, assert_equal, assert_raises, raises,
                        assert_true, assert_false)

from landlab import RasterModelGrid


class TestRasterModelGridConnectingFaces():
    def setup(self):
        self.rmg = RasterModelGrid(4, 5)

    def test_horizontally_adjacent_cells(self):
        assert_array_equal(self.rmg.get_face_connecting_cell_pair(0, 1),
                           np.array([10]))

    def test_vertically_adjacent_cells(self):
        assert_array_equal(self.rmg.get_face_connecting_cell_pair(0, 3),
                           np.array([3]))

    def test_diagonally_adjacent_cells(self):
        assert_array_equal(self.rmg.get_face_connecting_cell_pair(1, 5),
                           np.array([]))

    def test_non_adjacent_cells(self):
        assert_array_equal(self.rmg.get_face_connecting_cell_pair(0, 2),
                           np.array([]))


class TestRasterModelGridCellFaces():
    def setup(self):
        self.rmg = RasterModelGrid(4, 5)

    def test_id_as_int(self):
        assert_array_equal(self.rmg.cell_faces(0), np.array([0, 9, 3, 10]))

    def test_id_as_array(self):
        assert_array_equal(self.rmg.cell_faces(np.array([0, 1])),
                           np.array([[0, 9, 3, 10], [1, 10, 4, 11]]))
