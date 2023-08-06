#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      heistermann
#
# Created:     08.11.2012
# Copyright:   (c) heistermann 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

##import wradlib
##import numpy as np
from enthought.mayavi import mlab
import pylab as pl
from scitools import *

if __name__ == '__main__':

    print "Running example for VPR..."

##    length = 10
##    x,y,z = vpr.meshgridN(range(length),range(length),range(length))
##    trg = np.vstack((x.ravel(), y.ravel(), z.ravel())).transpose()
##    src = np.vstack((np.arange(length), np.arange(length), np.arange(length))).transpose()
##    interpolator = ipol.Nearest(src, trg)
##    interpolated = interpolator(np.arange(length)).reshape(x.shape)
##    scene = mlab.points3d(x, y, z, interpolated)

    import wradlib
    import numpy as np
    # define elevation and azimuth angles, ranges, radar site coordinates, projection
    elevs  = np.array([0.5,1.5,2.4,3.4,4.3,5.3,6.2,7.5,8.7,10,12,14,16.7,19.5])
    azims  = np.arange(0., 360., 1.)
    ranges = np.arange(0., 120000., 1000.)
    sitecoords = (14.924218,120.255547,500.)
    projstr = wradlib.georef.create_projstr("utm", zone=51, hemisphere="north")
    # create Cartesian coordinates corresponding the location of the polar volume bins
    polxyz  = wradlib.vpr.volcoords_from_polar(sitecoords, elevs, azims, ranges, projstr)
    poldata = wradlib.vpr.synthetic_polar_volume(polxyz)
    # this is the shape of our polar volume
    polshape = (len(elevs),len(azims),len(ranges))
    # now we define the coordinates for the 3-D grid (the CAPPI layers)
    x = np.linspace(polxyz[:,0].min(), polxyz[:,0].max(), 120)
    y = np.linspace(polxyz[:,1].min(), polxyz[:,1].max(), 120)
    z = np.arange(500.,10500.,500.)
    xyz = wradlib.util.gridaspoints(x, y, z)
    gridshape = (len(x), len(y), len(z))

    # create an instance of the CAPPI class and use it to create a series of CAPPIs
    gridder = wradlib.vpr.CAPPI(polxyz, xyz, maxrange=ranges.max(), polshape=polshape, Ipclass=wradlib.ipol.Idw)
    gridded = np.ma.masked_invalid( gridder(poldata) ).reshape(gridshape)

    # plot results
    levels = np.linspace(0,100,25)
    wradlib.vis.plot_max_plan_and_vert(x, y, z, gridded, levels=levels, cmap=pl.cm.spectral)


##    pl.imshow(np.transpose(np.ma.masked_invalid(cartdata)[:,:,5]), origin="lower", interpolation="nearest")
##    pl.colorbar()
##    pl.show()


##    cartdata[cartdata>15.] = np.nan
##    cartdata = np.ma.masked_less(cartdata, 15.)
##    mlab.points3d(trg[:,0], trg[:,1], trg[:,2], cartdata.ravel(), scale_factor=1.)
##    mlab.contour3d(trg[:,0].reshape(gridshape), trg[:,1].reshape(gridshape), trg[:,2].reshape(gridshape), cartdata.reshape(gridshape))
##    mlab.contour3d(cartdata.reshape(gridshape))
##    scene = mlab.points3d(coords[:,0], coords[:,1], coords[:,2], data.ravel())

##    mlab.pipeline.image_plane_widget(mlab.pipeline.scalar_field(cartdata),
##                            plane_orientation='x_axes',
##                            slice_index=10,
##                        )
##    mlab.pipeline.image_plane_widget(mlab.pipeline.scalar_field(cartdata),
##                            plane_orientation='y_axes',
##                            slice_index=10,
##                        )
##    mlab.outline()
