#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Simple usage for geoloc.
"""

import numpy as np
from datetime import datetime
from pyorbital.geoloc import ScanGeometry, compute_pixels, get_lonlatalt
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

tle1 = "1 33591U 09005A   12345.45213434  .00000391  00000-0  24004-3 0  6113"
tle2 = "2 33591 098.8821 283.2036 0013384 242.4835 117.4960 14.11432063197875"

t = datetime(2012, 12, 12, 4, 16, 1, 575000)
scanline_nb = 100


def amsua(scans_nb, edges_only=False):
    """ Describe AMSU-A instrument geometry
    
    Parameters:
       scans_nb | int -  number of scan lines
     
     Keywords:
     * edges_only - use only edge pixels

    Returns:
       pyorbital.geoloc.ScanGeometry object
    
    """

    scan_len  = 30 # 30 samples per scan
    scan_rate = 8 # single scan, seconds
    scan_angle = -48.3 # swath, degrees
    sampling_interval = 0.2 # single view, seconds
    sync_time = 0.00355 # delay before the actual scan starts

    if edges_only:
        scan_points = np.array([0, scan_len])
    else:
        scan_points = np.arange(0, scan_len)

	# build the instrument (scan angles)
    samples = np.vstack(((scan_points - (scan_len*0.5-0.5)) / (scan_len*0.5) * np.deg2rad(scan_angle),
	                   np.zeros((len(scan_points),)))).transpose()
    samples = np.tile(samples, [scans_nb, 1])

	# building the corresponding times array
    offset = np.arange(scans_nb) * scan_rate
    times = (np.tile(scan_points * sampling_interval + sync_time, [scans_nb, 1])
	         + np.expand_dims(offset, 1))

	# build the scan geometry object
    return ScanGeometry(samples, times.ravel())



# build the scan geometry object
sgeom = amsua(scanline_nb, edges_only=False)


#sgeom = ScanGeometry(amsua, amsua_times.ravel())
# roll, pitch, yaw in radians
rpy = (0, 0, 0)

# print the lonlats for the pixel positions
s_times = sgeom.times(t)
pixels_pos = compute_pixels((tle1, tle2), sgeom, s_times, rpy)
pos_time = get_lonlatalt(pixels_pos, s_times)

m = Basemap(projection='stere', llcrnrlat=24, urcrnrlat=70, llcrnrlon=-25, urcrnrlon=120, lat_ts=58, lat_0=58, lon_0=14, resolution='l')
#m = Basemap(projection='ortho',lat_0=45,lon_0=20,resolution='l')


# convert and plot the predicted pixels in red
x, y = m(pos_time[0], pos_time[1])
p1 = m.plot(x,y, marker='+', color='red', markerfacecolor='red', markeredgecolor='red', markersize=1, markevery=1, zorder=4, linewidth=0.0)
m.fillcontinents(color='0.85', lake_color=None, zorder=3)
m.drawparallels(np.arange(-90.,90.,5.), labels=[1,0,1,0],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=1)
m.drawmeridians(np.arange(-180.,180.,5.), labels=[0,1,0,1],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=2)

plt.show()
