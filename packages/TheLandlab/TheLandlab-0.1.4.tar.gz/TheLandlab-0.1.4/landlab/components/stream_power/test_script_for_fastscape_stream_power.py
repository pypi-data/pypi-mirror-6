#! /usr/env/python

"""
test_script_for_fastscape_stream_power.py: 
    
Tests and illustrates use of route_flow_dn component.
"""

from landlab import RasterModelGrid
from landlab.components.flow_routing.route_flow_dn import FlowRouter
from landlab.io import read_esri_ascii
from landlab.plot.imshow import imshow_node_grid
import os
import pylab
from numpy import ones, size

dem_name = '../../io/tests/data/west_bijou_gully.asc'
outlet_row = 82
outlet_column = 38

# Read in a DEM and set its boundaries (we'll try this one later)
DATA_FILE = os.path.join(os.path.dirname(__file__), dem_name)
(dem_grid, z) = read_esri_ascii(DATA_FILE)
dem_grid.set_nodata_nodes_to_inactive(z, 0) # set nodata nodes to inactive bounds
outlet_node = dem_grid.grid_coords_to_node_id(outlet_row, outlet_column)

grid = RasterModelGrid(4, 5, 1.0)
grid.set_inactive_boundaries(True, False, True, True)
z = grid.add_zeros('node', 'Land_Surface__Elevation')
z[6] = 4.5
z[7] = 3.
z[8] = 1.
z[11] = 4.
z[12] = 2.8
z[13] = 2.


# Get array of interior (active) node IDs
interior_nodes = grid.get_active_cell_node_ids()

# Route flow
flow_router = FlowRouter(grid)
r, a, q, ss, s, rl = flow_router.route_flow(z)

for i in range(grid.number_of_nodes):
    print i, grid.node_x[i], grid.node_y[i], z[i], grid.node_status[i], \
          r[i], a[i], q[i], ss[i], rl[i]

# Let's take a look for debugging
#print 'node  receiver  flow_link'
#for i in interior_nodes:
#    print i, r[i], rl[i]

# Calculate lengths of flow links
flow_link_length = ones(size(z))
flow_link_length[interior_nodes] = grid.link_length[rl[interior_nodes]]
print 'fll:', flow_link_length

# Get a 2D array version of the elevations
ar = grid.node_vector_to_raster(a)

numcols = grid.number_of_node_columns
numrows = grid.number_of_node_rows
dx = grid.dx

# Create a shaded image
pylab.close()  # clear any pre-existing plot
im = pylab.imshow(ar, cmap=pylab.cm.RdBu, extent=[0,numcols*dx,0,numrows*dx])
# add contour lines with labels
cset = pylab.contour(ar, extent=[0,numcols*dx,numrows*dx,0])
pylab.clabel(cset, inline=True, fmt='%1.1f', fontsize=10)
    
# add a color bar on the side
cb = pylab.colorbar(im)
cb.set_label('Drainage area, sq meters')
    
# add a title and axis labels
pylab.title('DEM')
pylab.xlabel('Distance (m)')
pylab.ylabel('Distance (m)')

# Display the plot
pylab.show()


# HERE IS THE STREAM POWER PART

import numpy

K = 0.00001
dt = 100.0
m = 0.5
num_time_steps = 1

# Derived parameters
Kdt = K*dt  # saves lots of multiplying later

# Time loop
for t in range(num_time_steps):
    
    # Update baselevel nodes if applicable
    # (to be added)

    # Calculate A^m and K A^m dt / L using Numpy array operations, for speed
    # (TODO: flow router should return an array of flow-link lengths)
    Am = numpy.power(a, m)
    alpha = Kdt*Am/flow_link_length

    # Loop over nodes from downstream to upstream, updating elevations using 
    # analytical solution (implicit)
    for i in s:  # for each node ID, in order from downstream to upstream
        
        j = r[i]   # receiver (downstream node) of i
        print i, j
        if i != j:  # if sender and receiver are same, it's a boundary node
            z[i] += alpha[i]*z[j]/(1.0+alpha[i])

