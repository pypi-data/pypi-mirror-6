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

import wradlib
import numpy as np
import pylab as pl
from phiradarqpe.phi_main import _make_cappi_coords


if __name__ == '__main__':

    print "Running example to retrieve average VPR..."
    fname = r"E:\test\vprtest\Rmean_TAG_201208080000-201208080600.polvol"
    polvol, polmetadata = wradlib.io.from_hdf5(fname)
    projstr = wradlib.georef.create_projstr("utm", zone=51, hemisphere="north")
    sitecoords = polmetadata["sitecoords"]
    elevs = polmetadata["elevs"]
    azims = polmetadata["azims"]
    ranges = polmetadata["ranges"]

    # create Cartesian coordinates corresponding the location of the polar volume bins
##    polxyz  = wradlib.vpr.volcoords_from_polar(sitecoords, elevs, azims, ranges, projstr)
##    poldata = polvol#wradlib.vpr.synthetic_polar_volume(polxyz)
    # this is the shape of our polar volume
    polshape = (len(elevs),len(azims),len(ranges))

    # now we define the coordinates for the 3-D grid (the CAPPI layers)
    z = np.arange(1000.,8000.,200.)

    polxyz, xyz, cappimeta = _make_cappi_coords(polmetadata, z, 240, projstr, polmetadata["sitecoords"])
    gridshape = cappimeta["shape"]

##    xyz = wradlib.util.gridaspoints(x, y, z)
##    gridshape = (len(z), len(y), len(x))

    # create an instance of the CAPPI class and use it to create a series of CAPPIs
    gridder = wradlib.vpr.CAPPI(polxyz, xyz, maxrange=ranges.max(), minelev=0.5, maxelev=19.5, gridshape=gridshape,
                                Ipclass=wradlib.ipol.Nearest)

    gridded = gridder(polvol.ravel()).reshape(gridshape)

    ix = np.where(np.logical_or(gridded[6,...].ravel()<4, np.isnan(gridded[6,...].ravel())))[0]
    print 240*240-len(ix)

    gridded2 = gridded.copy()
    gridded2 = gridded2.reshape(len(z),-1)
    gridded2[:,ix] = np.nan
    gridded2 = gridded2.reshape(gridded.shape)

    gridded = np.ma.masked_invalid( gridded)

    gridded2 = np.ma.masked_invalid( gridded2)

##    vpr2d = wradlib.vpr.mean_norm_vpr_from_volume(gridded, 0)

    tmp = gridded2 / gridded2[2]
    vpr1d = np.mean(tmp.reshape((len(z), -1)), axis=1)
    pl.plot(vpr1d, z)
    pl.show()
##
    x = np.linspace(polxyz[:,0].min(), polvol[:,0].max(), 240)
    y = np.linspace(polxyz[:,1].min(), polxyz[:,1].max(), 240)

    # plot results
    levels = np.linspace(0,100,25)
    wradlib.vis.plot_max_plan_and_vert(z, y, x, gridded2*6, levels=levels, cmap=pl.cm.spectral)



