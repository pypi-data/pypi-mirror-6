#! /usr/bin/env python
"""
Unit tests for landlab.io.netcdf module.
"""

import unittest
import os
import numpy as np
from StringIO import StringIO

from landlab.io.netcdf import read_netcdf


_TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestReadNetcdf(unittest.TestCase):
    def test_read_netcdf3_64bit(self):
        grid = read_netcdf(os.path.join(_TEST_DATA_DIR, 'test-netcdf3-64bit.nc'))
        self.assertEqual(grid.shape, (4, 3))

    def test_read_netcdf4(self):
        grid = read_netcdf(os.path.join(_TEST_DATA_DIR, 'test-netcdf4.nc'))
        self.assertEqual(grid.shape, (4, 3))


if __name__ == '__main__':
    unittest.main()
