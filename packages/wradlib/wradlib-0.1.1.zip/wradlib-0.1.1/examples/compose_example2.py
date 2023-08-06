#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      heistermann
#
# Created:     21.02.2012
# Copyright:   (c) heistermann 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import wradlib.io as io
import wradlib.ipol as ipol
import wradlib.qual as qual
import wradlib.comp as comp
import wradlib.georef as georef
import wradlib.vis as vis
import numpy as np
import pylab as pl
from matplotlib import mpl
from mpl_toolkits.basemap import Basemap, cm

if __name__ == '__main__':

    #---------------------------------------------------------------------------
    # We start with one radar, only
    #---------------------------------------------------------------------------

    fname='E:/data/philippines/radar/Netcdf 0926_2011_00H/SUB-20110926-000549-01-Z.nc'
    rad1, attrs1 = io.read_EDGE_netcdf(fname)
    rad1         = rad1.ravel()
    rad1[np.isnan(rad1)]=0.
    r            = attrs1['r']
    az           = attrs1['az']
    sitecoords   = attrs1['sitecoords']
    projstr      = "+proj=utm +zone=51 +ellps=WGS84"

##    vis.polar_plot(rad1.reshape((len(az),len(r))))

##    rad1 = np.loadtxt('data/polar_dBZ_tur.gz').ravel()
##    # 1st step: generate the centroid coordinates of the radar bins
##    #   define the polar coordinates and the site coordinates in lat/lon
##    r = np.arange(1,129)
##    az = np.linspace(0,360,361)[0:-1]
##    #   drs:  51.12527778 ; fbg: 47.87444444 ; tur: 48.58611111 ; muc: 48.3372222
##    #   drs:  13.76972222 ; fbg: 8.005 ; tur: 9.783888889 ; muc: 11.61277778
##    sitecoords = (48.5861, 9.7839)
##    projstr = '''
##    +proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=bessel
##    +towgs84=598.1,73.7,418.2,0.202,0.045,-2.455,6.7 +units=m +no_defs
##    '''

    rad1x, rad1y = georef.projected_bincoords_from_radarspecs(r, az, sitecoords, projstr)
    center1 = [rad1x.mean(), rad1y.mean()]
    radius1 = 480000.

    # define spatial bounding box of the grid
    bbox={'lllon':119.5,'lllat':13.5,'urlon':122.0,'urlat':16.5}
    xminmax, yminmax = georef.project([bbox['lllat'], bbox['urlat']], [bbox['lllon'], bbox['urlon']], projstr)
    def makegrid(xmin, xmax, ymin, ymax, width=1000.):
        x = np.arange(xmin, xmax, width)
        y = np.arange(ymin, ymax, width)
        coords = np.meshgrid(x,y)
        gridshape = coords[0].shape
        coords = np.vstack((coords[0].ravel(), coords[1].ravel())).transpose()
        return coords, gridshape
    coords, gridshape = makegrid(xminmax[0], xminmax[1], yminmax[0], yminmax[1])
#    coords, gridshape = makegrid(rad1x.min(), rad1x.max(), rad1y.min(), rad1y.max())
#    coords, gridshape = makegrid(xminmax[0], xminmax[0]+250000., yminmax[0], yminmax[0]+200000.)


    # transfer the radar data from the polar coordinates to the target grid
    rad1coords = np.vstack((rad1x, rad1y)).transpose()
    rad1_gridded = comp.togrid(rad1coords, coords, radius1, center1, rad1, ipol.Nearest)

    print gridshape

##    pl.pcolormesh( coords[:,0].reshape(gridshape), coords[:,1].reshape(gridshape), np.ma.masked_invalid(rad1_gridded.reshape(gridshape)) )
##    pl.show()



    # define spatial bounding box of the Basemap
##    bbox={'llcrnrlon':np.min(polygons[:,:,0]),
##              'llcrnrlat':np.min(polygons[:,:,1]),
##              'urcrnrlon':np.max(polygons[:,:,0]),
##              'urcrnrlat':np.max(polygons[:,:,1])}

    lon0=sitecoords[1]
    lat0=sitecoords[0]
    # create figure and axes instances
    fig = pl.figure(figsize=(8,8))
    ax = fig.add_axes([0.1,0.1,0.8,0.8])
    # create polar stereographic Basemap instance.
    m = Basemap(llcrnrlon=bbox['lllon'],llcrnrlat=bbox['lllat'],
                            urcrnrlon=bbox['urlon'],urcrnrlat=bbox['urlat'],
                        resolution='i',projection='tmerc',lat_0=lat0, lon_0=lon0)    # draw coastlines, state and country boundaries, edge of map.
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    # draw parallels.
    parallels = np.arange(0.,90,10.)
    m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)
    # draw meridians
    meridians = np.arange(180.,360.,10.)
    m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)
    lons, lats = georef.project(coords[:,1], coords[:,0], projstr, True)
##    ny = data.shape[0]; nx = data.shape[1]
##    lons, lats = m.makegrid(256, 256) # get lat/lons of ny by nx evenly space grid.
    x, y = m(lons, lats) # compute map proj coordinates.
    # draw filled contours.
    clevs = [-100,0,10,20,30,40,45,50,55,60,65]
    cs = m.pcolormesh(x.reshape(gridshape), y.reshape(gridshape), np.ma.masked_invalid(rad1_gridded.reshape(gridshape)))
    # add colorbar.
    cbar = m.colorbar(cs,location='bottom',pad="5%")
    cbar.set_label('dbZ')
    # add title
    pl.title('title')
    pl.show()





