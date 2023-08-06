#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, 2013, 2014 Martin Raspaud

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

"""Testing the geolocation module of pyorbital.
"""



from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

from pyorbital.geoloc_instrument_definitions import avhrr

from pyorbital.geoloc import *
from mpop.satellites import PolarFactory

def plot(lons1, lats1, lons2, lats2):
    m = Basemap(projection='stere', llcrnrlat=14, urcrnrlat=60, llcrnrlon=-25, urcrnrlon=120, lat_ts=58, lat_0=58, lon_0=14, resolution='l')


    # convert and plot the predicted pixels in red
    x, y = m(lons1, lats1)
    p1 = m.plot(x,y, marker='+', color='red', markerfacecolor='red', markeredgecolor='red', markersize=1, markevery=1, zorder=4, linewidth=0.0)

    x, y = m(lons2, lats2)
        
    p2 = m.plot(x,y, marker='+', color='blue', markerfacecolor='blue', markeredgecolor='blue', markersize=1, markevery=1, zorder=4, linewidth=0.0)

    m.fillcontinents(color='0.85', lake_color=None, zorder=3)
    m.drawparallels(np.arange(-90.,90.,5.), labels=[1,0,1,0],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=1)
    m.drawmeridians(np.arange(-180.,180.,5.), labels=[0,1,0,1],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=2)

    plt.show()


def cached_lonlats(scene):
    flon = "/tmp/lons" + str(scene.time_slot) + ".npy"
    flat = "/tmp/lats" + str(scene.time_slot) + ".npy"
    try:
        lons, lats = np.load(flon), np.load(flat)
    except IOError:

        scene.load()
        lons = scene.area.lons[:, 24:2048:40]
        lats = scene.area.lats[:, 24:2048:40]

        print lons.shape

        np.save(flon, lons)
        np.save(flat, lats)
    return lons, lats
    

def test_case_1():
    
    tle1 = "1 26536U 00055A   13076.42963155  .00000201  00000-0  13237-3 0  1369"
    tle2 = "2 26536  99.0540 128.2392 0010826  39.9070  85.2960 14.12848373643614"
    scanline_nb = 5680
    scan_points = np.arange(24, 2048, 40)

    #t = datetime(2013, 3, 18, 8, 15, 21, 186000)
    t = datetime(2013, 3, 18, 8, 15, 22, 352000)
    #t = datetime(2013, 3, 18, 8, 15, 23, 186000)


    sgeom = avhrr(scanline_nb, scan_points, 55.25)

    rpy = [np.deg2rad(-37.0/1000), np.deg2rad(-11.0/1000), np.deg2rad(146.0/1000)]
    #rpy = [0, 0, 0]
    s_times = sgeom.times(t)
    print (s_times[25::51])
    pixels_pos = compute_pixels((tle1, tle2), sgeom, s_times, rpy)
    pos_time = get_lonlatalt(pixels_pos, s_times)

    g = PolarFactory.create_scene("noaa", "16", "avhrr", t, orbit="64374")

    lons, lats = cached_lonlats(g)

    print np.sqrt(np.max(lons - pos_time[0].reshape(lons.shape)) ** 2 + np.max(lats - pos_time[1].reshape(lats.shape)) ** 2)
    print "max", np.max(abs(lons - pos_time[0].reshape(lons.shape)))
    print "max", np.max(abs(lats - pos_time[1].reshape(lats.shape)))

    plot(pos_time[0], pos_time[1], lons, lats)

def test_case_5():

    tle1 = "1 28654U 05018A   08167.42204778 -.00000193  00000-0 -82304-4 0  4671"
    tle2 = "2 28654  98.8667 108.3736 0013786 323.0689  36.9527 14.11168946158226"

    scanline_nb = 5121
    scan_points = np.arange(24, 2048, 40)

    t = datetime(2008, 6, 16, 11, 48, 48, 616000)


    sgeom = avhrr(scanline_nb, scan_points)
    # 171, 105, 32
    #rpy = [np.deg2rad(-37.0/1000), np.deg2rad(-11.0/1000), np.deg2rad(146.0/1000)]
    rpy = [0, 0, 0]
    rpy = [np.deg2rad(171.0/1000), np.deg2rad(105.0/1000), np.deg2rad(32.0/1000)]
    s_times = sgeom.times(t)
    pixels_pos = compute_pixels((tle1, tle2), sgeom, s_times, rpy)
    pos_time = get_lonlatalt(pixels_pos, s_times)

    g = PolarFactory.create_scene("noaa", "18", "avhrr", t, orbit="15838")

    lons, lats = cached_lonlats(g)

    print np.sqrt(np.max(lons - pos_time[0].reshape(lons.shape)) ** 2 + np.max(lats - pos_time[1].reshape(lats.shape)) ** 2)
    print "max", np.max(abs(lons - pos_time[0].reshape(lons.shape)))
    print "max", np.max(abs(lats - pos_time[1].reshape(lats.shape)))

    plot(pos_time[0], pos_time[1], lons, lats)

def test_case_2():
    
    tle1 = "1 33591U 09005A   12345.45213434  .00000391  00000-0  24004-3 0  6113"
    tle2 = "2 33591 098.8821 283.2036 0013384 242.4835 117.4960 14.11432063197875"
    scanline_nb = 351
    scan_points = np.arange(24, 2048, 40)

    t = datetime(2012, 12, 12, 4, 16, 1, 575000)

    sgeom = avhrr(scanline_nb, scan_points)

    rpy = (0, 0, 0)
    
    s_times = sgeom.times(t)
    pixels_pos = compute_pixels((tle1, tle2), sgeom, s_times, rpy)
    pos_time = get_lonlatalt(pixels_pos, s_times)

    g = PolarFactory.create_scene("noaa", "19", "avhrr", t, orbit="19812")

    lons, lats = cached_lonlats(g)

    print np.sqrt(np.max(lons - pos_time[0].reshape(lons.shape)) ** 2 + np.max(lats - pos_time[1].reshape(lats.shape)) ** 2)
    print "max", np.max(abs(lons - pos_time[0].reshape(lons.shape)))
    print "max", np.max(abs(lats - pos_time[1].reshape(lats.shape)))

    plot(pos_time[0], pos_time[1], lons, lats)

def test_case_3():
    
    tle1 = "1 33591U 09005A   12345.45213434  .00000391  00000-0  24004-3 0  6113"
    tle2 = "2 33591 098.8821 283.2036 0013384 242.4835 117.4960 14.11432063197875"
    scanline_nb = 351
    scan_points = np.arange(24, 2048, 40)

    t = datetime(2012, 12, 12, 4, 17, 1, 575000)

    sgeom = avhrr(scanline_nb, scan_points)

    rpy = (0, 0, 0)
    
    s_times = sgeom.times(t)
    pixels_pos = compute_pixels((tle1, tle2), sgeom, s_times, rpy)
    pos_time = get_lonlatalt(pixels_pos, s_times)

    g = PolarFactory.create_scene("noaa", "19", "avhrr", t, orbit="19812")

    lons, lats = cached_lonlats(g)

    print np.sqrt(np.max(lons - pos_time[0].reshape(lons.shape)) ** 2 + np.max(lats - pos_time[1].reshape(lats.shape)) ** 2)
    print "max", np.max(abs(lons - pos_time[0].reshape(lons.shape)))
    print "max", np.max(abs(lats - pos_time[1].reshape(lats.shape)))

    plot(pos_time[0], pos_time[1], lons, lats)

def test_case_4():
    
    tle1 = "1 26536U 00055A   12312.31001555  .00000182  00000-0  12271-3 0  9594"
    tle2 = "2 26536  99.0767 356.5209 0011007  44.1314 316.0725 14.12803055625240"
    scanline_nb = 5428
    scan_points = np.arange(24, 2048, 40)

    t = datetime(2012, 11, 7, 9, 33, 46, 526000)

    sgeom = avhrr(scanline_nb, scan_points, 55.25)

 
    rpy = [np.deg2rad(-9.0/1000), np.deg2rad(-199.0/1000), np.deg2rad(-11.0/1000)]    
    s_times = sgeom.times(t)
    pixels_pos = compute_pixels((tle1, tle2), sgeom, s_times, rpy)
    pos_time = get_lonlatalt(pixels_pos, s_times)

    g = PolarFactory.create_scene("noaa", "16", "avhrr", t, orbit="62526")

    lons, lats = cached_lonlats(g)

    print np.sqrt(np.max(lons - pos_time[0].reshape(lons.shape)) ** 2 + np.max(lats - pos_time[1].reshape(lats.shape)) ** 2)
    print "max", np.max(abs(lons - pos_time[0].reshape(lons.shape)))
    print "max", np.max(abs(lats - pos_time[1].reshape(lats.shape)))

    plot(pos_time[0], pos_time[1], lons, lats)




def test_viirs(t):
        #  TLE comes from ftp://is.sci.gsfc.nasa.gov/ancillary/ephemeris/tle/drl.tle.2012030213
    # NPP
    npp_tle1 = "1 37849U 05001A   12061.00019361  .00000000  00000-0 -31799-4 2    06"
    npp_tle2 = "2 37849 098.7082 000.2437 0000785 084.9351 038.5818 14.19547815017683"


    # npp scanlines @ 375m
    # the sensor scans 48 taking 32 pixels at once (so the height of granule is 48 * 32 = 1536 pixels)
    scanline_nb = 48

    # building the npp angles, 6400 pixels from +55.84 to -55.84 degrees zenith
    #npp = np.vstack(((np.arange(6400) - 3199.5) / 3200 * np.deg2rad(-55.84), np.zeros((6400,)))).transpose()
    #npp = np.tile(npp, [scanline_nb, 1])

    #scan_pixels = 32
    #taking just borders and middle for now
    scan_pixels = 3
    #scan_pixels = 1

    across_track = (np.arange(6400) - 3199.5) / 3200 * np.deg2rad(-55.84)
    #npp = np.tile(npp_line_y, [scan_pixels, 1])

    # y rotation: np.arctan2(11.87/2, 824.0)

    y_max_angle = np.arctan2(11.87/2, 824.0)
    along_track = np.array([-y_max_angle, 0, y_max_angle])
    #along_track = np.array([0])

    scan = np.vstack((np.tile(across_track, scan_pixels),
                      np.repeat(along_track, 6400))).T
    
    npp = np.tile(scan, [scanline_nb, 1])

    # from the timestamp in the filenames, a granule takes 1:25.400 to record (85.4 seconds)
    # so 1.779166667 would be the duration of 1 scanline
    # dividing the duration of a single scan by a width of 6400 pixels results in 0.0002779947917 seconds for each column of 32 pixels in the scanline
    # what is the 0.0025415??  this still comes from the AVHRR example at github

    # the individual times per pixel are probably wrong, unless the scanning behaves the same as for AVHRR, The VIIRS sensor rotates to allow internal calibration before each scanline. This would imply that the scanline always moves in the same direction.
    # more info @ http://www.eoportal.org/directory/pres_NPOESSNationalPolarorbitingOperationalEnvironmentalSatelliteSystem.html

    offset = np.arange(scanline_nb) * 1.779166667
    #times = (np.tile(np.arange(6400) * 0.0002779947917 + 0.0025415, [scanline_nb, 1]) + np.expand_dims(offset, 1))

    times = (np.tile(np.arange(6400) * 0.0002779947917, [scanline_nb, scan_pixels]) + np.expand_dims(offset, 1))

    # build the scan geometry object
    sgeom = ScanGeometry(npp, times.ravel())

    # get the pixel locations
    stimes = sgeom.times(t)
    pixels_pos = compute_pixels((npp_tle1, npp_tle2), sgeom, stimes)

    pos_time = get_lonlatalt(pixels_pos, stimes)
    return pixels_pos, pos_time, sgeom

def global_test_viirs():
    ### VIIRS


   # starttime is taken from filename of the 'target' granule

    t = datetime(2012, 3, 2, 12, 27, 23)
    #    t2 = datetime.datetime(2012, 3, 2, 12, 27, 23) + timedelta(seconds=85.4)

    pixels_pos, pos_time, sg1 = test_viirs(t)
    #    pixels_pos2, pos_time2, sg2 = test_viirs(t2)
    import cProfile, pstats
    cProfile.run('test_viirs(t)', "fooprof")
    p = pstats.Stats('fooprof')
    p.sort_stats('time').print_stats()


    # Mercator map centered above the target granule, near South Africa
    m = Basemap(projection='merc',llcrnrlat=-45,urcrnrlat=-25,llcrnrlon=0,urcrnrlon=40,lat_ts=-35,resolution='l')

    # convert and plot the predicted pixels in red
    x, y = m(pos_time[0],pos_time[1])
    p1 = m.plot(x,y, marker='+', color='red', markerfacecolor='red', markeredgecolor='red', markersize=1, markevery=1, zorder=4, linewidth=0.0)

    # read the validation data from CSV, its lat and lon from the outer pixel edge in the geolocation file
    # source: GITCO_npp_d20120302_t1227233_e1228475_b01789_c20120303154859293970_noaa_ops.h5

    #bound = np.genfromtxt('D:\\GITCO_npp_d20120302_t1227233_e1228475_b01789_c20120303154859293970_noaa_ops_outer_edge.csv', delimiter=',', names=True)

    # convert and plot validation data in blue
    #tmpx, tmpy = m(bound['Lon'],bound['Lat'])
    #p2 = m.plot(tmpx,tmpy, marker='o', color='blue', markerfacecolor='blue', markeredgecolor='blue', markersize=0.1, markevery=1, zorder=5, linewidth=0.0)


    # general map beautification

    m.fillcontinents(color='0.85', lake_color=None, zorder=3)
    m.drawparallels(np.arange(-90.,90.,5.), labels=[1,0,1,0],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=1)
    m.drawmeridians(np.arange(-180.,180.,5.), labels=[0,1,0,1],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=2)

    plt.title('NPP Granule (Start at 2012-03-02 12:27:23)')
    #    plt.show()
    #plt.savefig('granule_test.png', dpi=400)
    plt.show()


if __name__ == '__main__':
    test_case_5()

