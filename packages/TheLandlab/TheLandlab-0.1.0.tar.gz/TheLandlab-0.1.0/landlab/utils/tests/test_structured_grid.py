#! /usr/bin/env python

import unittest
import numpy as np

from landlab.testing import NumpyArrayTestingMixIn

import landlab.utils.structured_grid as sgrid
from landlab.utils.structured_grid import BAD_INDEX_VALUE


class TestGetNodeCoords(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_node_x_2d(self):
        (x, _) = sgrid.node_coords((3,2))

        self.assertArrayEqual(x, np.array([0., 1.,
                                        0., 1.,
                                        0., 1.,]))

    def test_node_x_2d_with_spacing(self):
        (x, _) = sgrid.node_coords((3,2), (2., 10.))

        self.assertArrayEqual(x, np.array([0., 10.,
                                        0., 10.,
                                        0., 10.,]))

    def test_node_x_2d_with_origin(self):
        (x, _) = sgrid.node_coords((3,2), (2., 10.), (-1., 1.))

        self.assertArrayEqual(x, np.array([1., 11.,
                                        1., 11.,
                                        1., 11.,]))

    def test_node_y_2d(self):
        (_, y) = sgrid.node_coords((3,2))

        self.assertArrayEqual(y, np.array([0., 0.,
                                        1., 1.,
                                        2., 2.,]))

    def test_node_y_2d_with_spacing(self):
        (_, y) = sgrid.node_coords((3,2), (2., 10.))

        self.assertArrayEqual(y, np.array([0., 0.,
                                        2., 2.,
                                        4., 4.,]))

    def test_node_y_2d_with_origin(self):
        (_, y) = sgrid.node_coords((3,2), (2., 10.), (-1., 1.))

        self.assertArrayEqual(y, np.array([-1., -1.,
                                         1.,  1.,
                                         3.,  3.,]))

    def test_round_off_error(self):
        (x, y) = sgrid.node_coords((135, 127),
                                   (5.4563957090392, 5.4563957090392),
                                   (0., 0.))

        self.assertTupleEqual(x.shape, (135 * 127, ))
        self.assertTupleEqual(y.shape, (135 * 127, ))


class TestGetCellNode(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_2d_shape_2_by_3(self):
        cell_nodes = sgrid.node_index_at_cells((2, 3))

        self.assertArrayEqual(cell_nodes, np.array([]))

    def test_2d_shape_3_by_3(self):
        cell_nodes = sgrid.node_index_at_cells((3, 3))

        self.assertArrayEqual(cell_nodes, np.array([4]))

    def test_shape_4_by_5(self):
        cell_nodes = sgrid.node_index_at_cells((4, 5))

        self.assertArrayEqual(cell_nodes, np.array([ 6,  7,  8,
                                                 11, 12, 13]))


class TestGetNodeLinks(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_2d_3_by_2_from_links(self):
        (from_indices, _) = sgrid.node_index_at_link_ends((3, 2))

        self.assertArrayEqual(from_indices,
                           np.array([0, 1, 2, 3,
                                     0, 2, 4]))

    def test_2d_3_by_2_to_links(self):
        (_, to_indices) = sgrid.node_index_at_link_ends((3, 2))

        self.assertArrayEqual(to_indices,
                           np.array([2, 3, 4, 5,
                                     1, 3, 5]))

    def test_west_links(self):
        links = sgrid.west_links((3, 4))
        self.assertArrayEqual(links,
                           np.array([[-1,  8,  9, 10],
                                     [-1, 11, 12, 13],
                                     [-1, 14, 15, 16]]))

        links = sgrid.west_links((1, 4))
        self.assertArrayEqual(links, np.array([[-1, 0, 1, 2]]))

        links = sgrid.west_links((4, 1))
        self.assertArrayEqual(links, np.array([[-1], [-1], [-1], [-1]]))

    def test_east_links(self):
        links = sgrid.east_links((3, 4))
        self.assertArrayEqual(links,
                           np.array([[ 8,  9, 10, -1],
                                     [11, 12, 13, -1],
                                     [14, 15, 16, -1]]))

        links = sgrid.east_links((1, 4))
        self.assertArrayEqual(links, np.array([[0, 1, 2, -1]]))

        links = sgrid.east_links((4, 1))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]).T)

    def test_north_links(self):
        links = sgrid.north_links((3, 4))
        self.assertArrayEqual(links, np.array([[ 0,  1,  2,  3],
                                            [ 4,  5,  6,  7],
                                            [-1, -1, -1, -1]]))

        links = sgrid.north_links((1, 4))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]))

        links = sgrid.north_links((4, 1))
        self.assertArrayEqual(links, np.array([[0, 1, 2, -1]]).T)

    def test_south_links(self):
        links = sgrid.south_links((3, 4))
        self.assertArrayEqual(links,
                           np.array([[-1, -1, -1, -1],
                                     [ 0,  1,  2,  3],
                                     [ 4,  5,  6,  7]]))

        links = sgrid.south_links((1, 4))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]))

        links = sgrid.south_links((4, 1))
        self.assertArrayEqual(links, np.array([[-1, 0, 1, 2]]).T)

    def test_inlinks(self):
        links = sgrid.inlinks((3, 4))
        self.assertArrayEqual(
            np.array([[-1, -1, -1, -1,  0,  1,  2,  3,  4,  5,  6,  7],
                      [-1,  8,  9, 10, -1, 11, 12, 13, -1, 14, 15, 16]]),
            links)

    def test_outlinks(self):
        links = sgrid.outlinks((3, 4))
        self.assertArrayEqual(
            np.array([[ 0,  1,  2,  3,  4,  5,  6,  7, -1, -1, -1, -1],
                      [ 8,  9, 10, -1, 11, 12, 13, -1, 14, 15, 16, -1]]),
            links)

class TestNodeActiveCell(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_one_active_cell(self):
        active_cells = sgrid.active_cell_index_at_nodes((3, 3))

        self.assertArrayEqual(
            active_cells,
            np.array([BAD_INDEX_VALUE, BAD_INDEX_VALUE, BAD_INDEX_VALUE,
                      BAD_INDEX_VALUE,               0, BAD_INDEX_VALUE,
                      BAD_INDEX_VALUE, BAD_INDEX_VALUE, BAD_INDEX_VALUE])
        )

    def test_no_active_cells(self):
        active_cells = sgrid.active_cell_index_at_nodes((3, 2))

        self.assertArrayEqual(
            active_cells,
            np.array([BAD_INDEX_VALUE, BAD_INDEX_VALUE,
                      BAD_INDEX_VALUE, BAD_INDEX_VALUE,
                      BAD_INDEX_VALUE, BAD_INDEX_VALUE])
        )
                                     
                                     
class TestActiveCells(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_one_active_cell(self):
        active_cells = sgrid.active_cell_index((3, 3))

        self.assertArrayEqual(active_cells, np.array([0]))

    def test_no_active_cells(self):
        active_cells = sgrid.active_cell_index((3, 2))

        self.assertArrayEqual(active_cells,
            np.array([]))


class TestCellCount(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_one_cell(self):
        n_cells = sgrid.cell_count((3, 3))
        self.assertEqual(n_cells, 1)

    def test_no_cells(self):
        n_cells = sgrid.cell_count((2, 3))
        self.assertEqual(n_cells, 0)


class TestInteriorCellCount(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_one_cell(self):
        n_cells = sgrid.interior_cell_count((3, 3))
        self.assertEqual(n_cells, 1)

    def test_no_cells(self):
        n_cells = sgrid.interior_cell_count((2, 3))
        self.assertEqual(n_cells, 0)


class TestActiveCellCount(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_one_cell(self):
        n_cells = sgrid.active_cell_count((3, 3))
        self.assertEqual(n_cells, 1)

    def test_no_cells(self):
        n_cells = sgrid.active_cell_count((2, 3))
        self.assertEqual(n_cells, 0)


class TestInteriorNodes(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_4_by_5(self):
        interiors = sgrid.interior_nodes((4, 5))
        self.assertArrayEqual(interiors, np.array([6, 7, 8, 11, 12, 13]))

    def test_no_interiors(self):
        interiors = sgrid.interior_nodes((2, 3))
        self.assertArrayEqual(interiors, np.array([]))


class TestNodeStatus(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_4_by_5(self):
        status = sgrid.node_status((4, 5))
        self.assertEqual(status.dtype, np.int8)
        self.assertArrayEqual(status,
                           np.array([1, 1, 1, 1, 1,
                                     1, 0, 0, 0, 1,
                                     1, 0, 0, 0, 1,
                                     1, 1, 1, 1, 1, ]))

    def test_no_interiors(self):
        status = sgrid.node_status((2, 3))
        self.assertEqual(status.dtype, np.int8)
        self.assertArrayEqual(status,
                           np.array([1, 1, 1,
                                     1, 1, 1,]))


class TestActiveLinks(unittest.TestCase, NumpyArrayTestingMixIn):
    """
    *--27-->*--28-->*--29-->*--30-->*
    ^       ^       ^       ^       ^
    10      11      12      13      14
    |       |       |       |       |
    *--23-->*--24-->*--25-->*--26-->*
    ^       ^       ^       ^       ^
    5       6       7       8       9   
    |       |       |       |       |
    *--19-->*--20-->*--21-->*--22-->*
    ^       ^       ^       ^       ^
    0       1       2       3       4
    |       |       |       |       |
    *--15-->*--16-->*--17-->*--18-->*
    """
    def test_4_by_5(self):
        active_links = sgrid.active_links((4, 5))
        self.assertArrayEqual(active_links,
                           np.array([1, 2, 3, 6, 7, 8, 11, 12, 13,
                                     19, 20, 21, 22, 23, 24, 25, 26]))
        self.assertEqual(len(active_links), sgrid.active_link_count((4, 5)))

    def test_with_node_status(self):
        status = sgrid.node_status((4, 5))
        status[6] = sgrid.INACTIVE_BOUNDARY
        active_links = sgrid.active_links((4, 5), node_status_array=status)

        self.assertArrayEqual(active_links,
                           np.array([2, 3, 7, 8, 11, 12, 13,
                                     21, 22, 23, 24, 25, 26]))

    def test_with_link_nodes(self):
        link_nodes = sgrid.node_index_at_link_ends((4, 5))
        active_links = sgrid.active_links((4, 5), link_nodes=link_nodes)

        self.assertArrayEqual(active_links,
                           np.array([1, 2, 3, 6, 7, 8, 11, 12, 13,
                                     19, 20, 21, 22, 23, 24, 25, 26]))
        self.assertEqual(len(active_links), sgrid.active_link_count((4, 5)))

    def test_vertical_active_link_count(self):
        link_count = sgrid.vertical_active_link_count((3, 4))
        self.assertEqual(4, link_count)

        link_count = sgrid.vertical_active_link_count((3, 2))
        self.assertEqual(0, link_count)

        node_status = np.ones((4, 5), dtype=np.int)
        link_count = sgrid.vertical_active_link_count((4, 5),
                                                      node_status=node_status)
        self.assertEqual(9, link_count)

        link_count = sgrid.vertical_active_link_count((4, 5),
                                                      node_status=node_status)
        node_status[0, 1] = 0
        link_count = sgrid.vertical_active_link_count((4, 5),
                                                      node_status=node_status)
        self.assertEqual(8, link_count)

        node_status[2, 1] = 0
        link_count = sgrid.vertical_active_link_count((4, 5),
                                                      node_status=node_status)
        self.assertEqual(6, link_count)

        node_status[2, 2] = 0
        link_count = sgrid.vertical_active_link_count((4, 5),
                                                      node_status=node_status)
        self.assertEqual(4, link_count)

        node_status[1, 1] = 0
        link_count = sgrid.vertical_active_link_count((4, 5),
                                                      node_status=node_status)
        self.assertEqual(4, link_count)

    def test_horizontal_active_link_count(self):
        link_count = sgrid.horizontal_active_link_count((3, 4))
        self.assertEqual(3, link_count)

        link_count = sgrid.horizontal_active_link_count((2, 3))
        self.assertEqual(0, link_count)

        node_status = np.ones((4, 5), dtype=np.int)
        link_count = sgrid.horizontal_active_link_count(
            (4, 5), node_status=node_status)
        self.assertEqual(8, link_count)

        link_count = sgrid.horizontal_active_link_count(
            (4, 5), node_status=node_status)
        node_status[0, 1] = 0
        link_count = sgrid.horizontal_active_link_count((4, 5),
                                                      node_status=node_status)
        self.assertEqual(8, link_count)

        node_status[2, 1] = 0
        link_count = sgrid.horizontal_active_link_count((4, 5),
                                                      node_status=node_status)
        self.assertEqual(6, link_count)

        node_status[2, 2] = 0
        link_count = sgrid.horizontal_active_link_count((4, 5),
                                                      node_status=node_status)
        self.assertEqual(5, link_count)

        node_status[1, 1] = 0
        link_count = sgrid.horizontal_active_link_count((4, 5),
                                                      node_status=node_status)
        self.assertEqual(3, link_count)

    def test_horizontal_active_link_ids(self):
        links = sgrid.horizontal_active_link_ids((3, 4))
        self.assertArrayEqual(links, np.array([[4, 5, 6]]))

        links = sgrid.horizontal_active_link_ids((1, 4))
        expected = np.array([], ndmin=2, dtype=np.int64)
        expected.shape = (0, 3)
        self.assertArrayEqual(expected, links)

        links = sgrid.horizontal_active_link_ids((4, 1))
        expected.shape = (2, 0)
        self.assertArrayEqual(expected, links)

        node_status = np.ones((4, 5), dtype=int)
        links = sgrid.horizontal_active_link_ids((4, 5),
                                                 node_status=node_status)
        self.assertArrayEqual(links, np.array([[ 9, 10, 11, 12],
                                            [13, 14, 15, 16]]))

        node_status = np.ones((4, 5), dtype=int)
        node_status[1, 1] = 0
        links = sgrid.horizontal_active_link_ids((4, 5),
                                                 node_status=node_status)
        self.assertArrayEqual(links, np.array([[-1, -1,  7,  8],
                                            [ 9, 10, 11, 12]]))

        node_status[2, 1] = 0
        links = sgrid.horizontal_active_link_ids((4, 5),
                                                 node_status=node_status)
        self.assertArrayEqual(links, np.array([[-1, -1, 6, 7],
                                            [-1, -1, 8, 9]]))

        node_status[0, 0] = 0
        links = sgrid.horizontal_active_link_ids((4, 5),
                                                 node_status=node_status)
        self.assertArrayEqual(links, np.array([[-1, -1, 6, 7],
                                            [-1, -1, 8, 9]]))

    def test_vertical_active_link_ids(self):
        links = sgrid.vertical_active_link_ids((3, 4))
        self.assertArrayEqual(links, np.array([[0, 1], [2, 3]]))

        links = sgrid.vertical_active_link_ids((1, 4))
        expected = np.array([], ndmin=2, dtype=np.int64)
        expected.shape = (0, 2)
        self.assertArrayEqual(expected, links)

        links = sgrid.vertical_active_link_ids((4, 1))
        expected.shape = (3, 0)
        self.assertArrayEqual(expected, links)

        node_status = np.ones((4, 5), dtype=int)
        links = sgrid.vertical_active_link_ids((4, 5), node_status=node_status)
        self.assertArrayEqual(links, np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]]))

        node_status = np.ones((4, 5), dtype=int)
        node_status[1, 1] = 0
        links = sgrid.vertical_active_link_ids((4, 5), node_status=node_status)
        self.assertArrayEqual(links,
                           np.array([[-1, 0, 1], [-1, 2, 3], [4, 5, 6]]))

        node_status[2, 1] = 0
        links = sgrid.vertical_active_link_ids((4, 5), node_status=node_status)
        self.assertArrayEqual(links,
                           np.array([[-1, 0, 1], [-1, 2, 3], [-1, 4, 5]]))

        node_status[0, 0] = 0
        links = sgrid.vertical_active_link_ids((4, 5), node_status=node_status)
        self.assertArrayEqual(links,
                           np.array([[-1, 0, 1], [-1, 2, 3], [-1, 4, 5]]))

    def test_west_links(self):
        links = sgrid.active_west_links((3, 4))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1],
                                            [-1,  4,  5,  6],
                                            [-1, -1, -1, -1]]))

        links = sgrid.active_west_links((1, 4))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]))

        links = sgrid.active_west_links((4, 1))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]).T)

    def test_east_links(self):
        links = sgrid.active_east_links((3, 4))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1],
                                            [ 4,  5,  6, -1],
                                            [-1, -1, -1, -1]]))

        links = sgrid.active_east_links((1, 4))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]))

        links = sgrid.active_east_links((4, 1))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]).T)

        links = sgrid.horizontal_active_link_ids((4, 5))
        self.assertArrayEqual(np.array([[9, 10, 11, 12],
                                     [13, 14, 15, 16]]),
                           links)

        links = sgrid.active_east_links((4, 5))
        self.assertArrayEqual(np.array([[-1, -1, -1, -1, -1],
                                     [ 9, 10, 11, 12, -1],
                                     [13, 14, 15, 16, -1],
                                     [-1, -1, -1, -1, -1]]),
                           links)

    def test_north_links(self):
        links = sgrid.active_north_links((3, 4))
        self.assertArrayEqual(links, np.array([[-1,  0,  1, -1],
                                            [-1,  2,  3, -1],
                                            [-1, -1, -1, -1]]))

        links = sgrid.active_north_links((1, 4))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]))

        links = sgrid.active_north_links((4, 1))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]).T)

    def test_south_links(self):
        links = sgrid.active_south_links((3, 4))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1],
                                            [-1,  0,  1, -1],
                                            [-1,  2,  3, -1]]))

        links = sgrid.active_south_links((1, 4))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]))

        links = sgrid.active_south_links((4, 1))
        self.assertArrayEqual(links, np.array([[-1, -1, -1, -1]]).T)

    def test_inlinks(self):
        links = sgrid.active_inlinks((3, 4))
        self.assertArrayEqual(
            np.array([[-1, -1, -1, -1, -1,  0,  1, -1, -1,  2,  3, -1],
                      [-1, -1, -1, -1, -1,  4,  5,  6, -1, -1, -1, -1]]),
            links)

    def test_outlinks(self):
        links = sgrid.active_outlinks((3, 4))
        self.assertArrayEqual(
            np.array([[-1,  0,  1, -1, -1,  2,  3, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1,  4,  5,  6, -1, -1, -1, -1, -1]]),
            links)

    def test_outlinks_4x5(self):
        links = sgrid.active_outlinks((4, 5))

        self.assertArrayEqual(np.array([[-1,  0,  1,  2, -1,
                                      -1,  3,  4,  5, -1,
                                      -1,  6,  7,  8, -1,
                                      -1, -1, -1, -1, -1],
                                     [-1, -1, -1, -1, -1,
                                      9, 10, 11, 12, -1,
                                      13, 14, 15, 16, -1,
                                      -1, -1, -1, -1, -1]]),
                           links)

    def test_inlinks_4x5(self):
        links = sgrid.active_inlinks((4, 5))

        self.assertArrayEqual(np.array([[-1, -1, -1, -1, -1,
                                      -1,  0,  1,  2, -1,
                                      -1,  3,  4,  5, -1,
                                      -1,  6, 7,  8, -1],
                                     [-1, -1, -1, -1, -1,
                                      -1,  9, 10, 11, 12,
                                      -1, 13, 14, 15, 16,
                                      -1, -1, -1, -1, -1]]),
                           links)


class TestFaces(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_face_count(self):
        self.assertEqual(17, sgrid.face_count((4, 5)))
        self.assertEqual(4, sgrid.face_count((3, 3)))
        self.assertEqual(0, sgrid.face_count((2, 100)))
        self.assertEqual(0, sgrid.face_count((100, 2)))
        self.assertEqual(0, sgrid.face_count((100, 1)))

    def test_active_face_count(self):
        self.assertEqual(17, sgrid.active_face_count((4, 5)))
        self.assertEqual(4, sgrid.active_face_count((3, 3)))
        self.assertEqual(0, sgrid.active_face_count((2, 100)))
        self.assertEqual(0, sgrid.active_face_count((100, 2)))
        self.assertEqual(0, sgrid.active_face_count((100, 1)))

    def test_active_faces(self):
        active_faces = sgrid.active_face_index((4, 5))
        self.assertArrayEqual(np.array([ 0,  1,  2,
                                      3,  4,  5,
                                      6,  7,  8,
                                      9, 10, 11, 12,
                                     13, 14, 15, 16]),
                           active_faces)


class TestLinkFaces(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_4_by_5(self):
        link_faces = sgrid.face_index_at_links((4, 5))

        BAD = sgrid.BAD_INDEX_VALUE

        self.assertArrayEqual(link_faces, np.array([BAD, 0, 1, 2, BAD,
                                                 BAD, 3, 4, 5, BAD,
                                                 BAD, 6, 7, 8, BAD,
                                                 BAD, BAD, BAD, BAD,
                                                 9, 10, 11, 12,
                                                 13, 14, 15, 16,
                                                 BAD, BAD, BAD, BAD]))

    def test_with_active_links(self):
        active_links = sgrid.active_links((4, 5))
        active_links = active_links[:-1]
        link_faces = sgrid.face_index_at_links((4, 5), actives=active_links)

        BAD = sgrid.BAD_INDEX_VALUE

        self.assertArrayEqual(link_faces, np.array([BAD, 0, 1, 2, BAD,
                                                 BAD, 3, 4, 5, BAD,
                                                 BAD, 6, 7, 8, BAD,
                                                 BAD, BAD, BAD, BAD,
                                                 9, 10, 11, 12,
                                                 13, 14, 15, BAD,
                                                 BAD, BAD, BAD, BAD]))


class TestReshapeArray(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_default(self):
        x = np.arange(12.)
        y = sgrid.reshape_array((3, 4), x)

        self.assertEqual(y.shape, (3, 4))
        self.assertArrayEqual(x, y.flat)
        self.assertTrue(y.flags['C_CONTIGUOUS'])
        self.assertIs(y.base, x)

    def test_copy(self):
        x = np.arange(12.)
        y = sgrid.reshape_array((3, 4), x, copy=True)

        self.assertEqual(y.shape, (3, 4))
        self.assertArrayEqual(x, y.flat)
        self.assertTrue(y.flags['C_CONTIGUOUS'])
        self.assertIsNone(y.base)

        y[0][0] = 0.
        self.assertArrayEqual(x, np.array([ 0.,  1.,  2., 3.,
                                         4.,  5.,  6., 7.,
                                         8.,  9., 10., 11.]))

    def test_flip(self):
        x = np.arange(12.)
        y = sgrid.reshape_array((3, 4), x, flip_vertically=True)

        self.assertEqual(y.shape, (3, 4))
        self.assertArrayEqual(y, np.array([[ 8.,  9., 10., 11.],
                                        [ 4.,  5.,  6., 7.],
                                        [ 0.,  1.,  2., 3.]]))
        self.assertFalse(y.flags['C_CONTIGUOUS'])
        self.assertIsNotNone(y.base)

        y[0][0] = 0.
        self.assertArrayEqual(x, np.array([ 0.,  1.,  2., 3.,
                                         4.,  5.,  6., 7.,
                                         0.,  9., 10., 11.]))

    def test_flip_copy(self):
        x = np.arange(12.)
        y = sgrid.reshape_array((3, 4), x, flip_vertically=True, copy=True)

        self.assertEqual(y.shape, (3, 4))
        self.assertArrayEqual(y, np.array([[ 8.,  9., 10., 11.],
                                        [ 4.,  5.,  6., 7.],
                                        [ 0.,  1.,  2., 3.]]))
        self.assertTrue(y.flags['C_CONTIGUOUS'])
        self.assertIsNot(y.base, x)


class TestDiagonalArray(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_default(self):
        diags = sgrid.diagonal_node_array((2, 3), out_of_bounds=-1)
        self.assertArrayEqual(diags,
                           np.array([[ 4, -1, -1, -1],
                                     [ 5,  3, -1, -1],
                                     [-1,  4, -1, -1],
                                     [-1, -1, -1,  1],
                                     [-1, -1,  0,  2],
                                     [-1, -1,  1, -1]]))

        self.assertTrue(diags.base is None)
        self.assertTrue(diags.flags['C_CONTIGUOUS'])

    def test_non_contiguous(self):
        diags = sgrid.diagonal_node_array((2, 3), out_of_bounds=-1,
                                          contiguous=False)
        self.assertArrayEqual(diags,
                           np.array([[ 4, -1, -1, -1],
                                     [ 5,  3, -1, -1],
                                     [-1,  4, -1, -1],
                                     [-1, -1, -1,  1],
                                     [-1, -1,  0,  2],
                                     [-1, -1,  1, -1]]))

        self.assertTrue(isinstance(diags.base, np.ndarray))
        self.assertFalse(diags.flags['C_CONTIGUOUS'])

    def test_boundary_node_mask_no_actives(self):
        diags = sgrid.diagonal_node_array((2, 3), out_of_bounds=-1,
                                          boundary_node_mask=-2)
        self.assertArrayEqual(diags, - 2 * np.ones((6, 4)))

    def test_boundary_node_mask(self):
        diags = sgrid.diagonal_node_array((3, 3), out_of_bounds=-1,
                                          boundary_node_mask=-2)
        self.assertArrayEqual(diags, 
                           np.array([[-2, -2, -2, -2], [-2, -2, -2, -2], [-2, -2, -2, -2],
                                     [-2, -2, -2, -2], [ 8,  6,  0,  2], [-2, -2, -2, -2],
                                     [-2, -2, -2, -2], [-2, -2, -2, -2], [-2, -2, -2, -2]]))


class TestNeighborArray(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_default(self):
        neighbors = sgrid.neighbor_node_array((2, 3))

        BAD = sgrid.BAD_INDEX_VALUE

        self.assertArrayEqual(
            neighbors,
            np.array([[  1,   3, BAD, BAD],
                      [  2,   4,   0, BAD],
                      [BAD,   5,   1, BAD],
                      [  4, BAD, BAD,   0],
                      [  5, BAD,   3,   1],
                      [BAD, BAD,   4,   2]]))

        self.assertTrue(neighbors.flags['C_CONTIGUOUS'])
        self.assertTrue(neighbors.base is None)

    def test_set_out_of_bounds(self):
        neighbors = sgrid.neighbor_node_array((2, 3), out_of_bounds=-1)
        self.assertArrayEqual(neighbors,
                           np.array([[ 1,  3, -1, -1],
                                     [ 2,  4,  0, -1],
                                     [-1,  5,  1, -1],
                                     [ 4, -1, -1,  0],
                                     [ 5, -1,  3,  1],
                                     [-1, -1,  4,  2]]))

    def test_as_view(self):
        neighbors = sgrid.neighbor_node_array((2, 3), out_of_bounds=-1,
                                              contiguous=False)
        self.assertArrayEqual(neighbors,
                           np.array([[ 1,  3, -1, -1],
                                     [ 2,  4,  0, -1],
                                     [-1,  5,  1, -1],
                                     [ 4, -1, -1,  0],
                                     [ 5, -1,  3,  1],
                                     [-1, -1,  4,  2]]))

        self.assertFalse(neighbors.flags['C_CONTIGUOUS'])
        self.assertTrue(isinstance(neighbors.base, np.ndarray))

    def test_boundary_node_mask_no_actives(self):
        neighbors = sgrid.neighbor_node_array((2, 3), out_of_bounds=-1,
                                          boundary_node_mask=-2)
        self.assertArrayEqual(neighbors, - 2 * np.ones((6, 4)))

    def test_boundary_node_mask(self):
        neighbors = sgrid.neighbor_node_array((3, 3), out_of_bounds=-1,
                                              boundary_node_mask=-2)
        self.assertArrayEqual(neighbors, 
                           np.array([[-2, -2, -2, -2], [-2, -2, -2, -2], [-2, -2, -2, -2],
                                     [-2, -2, -2, -2], [ 5,  7,  3,  1], [-2, -2, -2, -2],
                                     [-2, -2, -2, -2], [-2, -2, -2, -2], [-2, -2, -2, -2]]))


class TestInlinkMatrix(unittest.TestCase, NumpyArrayTestingMixIn):
    def test_no_inactive(self):
        inlinks = sgrid.setup_active_inlink_matrix((4, 5), return_count=False)
        self.assertArrayEqual(inlinks,
                           np.array([[-1, -1, -1, -1, -1,
                                      -1,  0,  1,  2, -1,
                                      -1,  3,  4,  5, -1,
                                      -1,  6,  7,  8, -1],
                                     [-1, -1, -1, -1, -1,
                                      -1,  9, 10, 11, 12,
                                      -1, 13, 14, 15, 16,
                                      -1, -1, -1, -1, -1]]))

    def test_inactive(self):
        status = np.ones((4, 5))
        status[1, 1] = 0
        inlinks = sgrid.setup_active_inlink_matrix((4, 5), return_count=False,
                                                   node_status=status)
        self.assertArrayEqual(inlinks,
                           np.array([[-1, -1, -1, -1, -1,
                                      -1, -1,  0,  1, -1,
                                      -1, -1,  2,  3, -1,
                                      -1,  4,  5,  6, -1],
                                     [-1, -1, -1, -1, -1,
                                      -1, -1, -1,  7,  8,
                                      -1,  9, 10, 11, 12,
                                      -1, -1, -1, -1, -1]]))

    def test_out_link_ids_at_nodes(self):
        links_ids = sgrid.outlink_index_at_node((4, 5))
        self.assertArrayEqual(
            np.array([[ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9,
                       10, 11, 12, 13, 14, -1, -1, -1, -1, -1],
                      [15, 16, 17, 18, -1, 19, 20, 21, 22, -1,
                       23, 24, 25, 26, -1, 27, 28, 29, 30, -1]]),
            links_ids)

    def test_in_link_ids_at_nodes(self):
        links_ids = sgrid.inlink_index_at_node((4, 5))
        self.assertArrayEqual(
            np.array([[-1, -1, -1, -1, -1,  0,  1,  2,  3,  4,
                        5,  6,  7,  8,  9, 10, 11, 12, 13, 14],
                      [-1, 15, 16, 17, 18, -1, 19, 20, 21, 22,
                       -1, 23, 24, 25, 26, -1, 27, 28, 29, 30]]),
            links_ids)


if __name__ == '__main__':
    unittest.main()
