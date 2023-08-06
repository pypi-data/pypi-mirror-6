#-------------------------------------------------------------------------------
# Name:        recipe1_clutter_attenuation_composition.py
# Purpose:
#
# Author:      heistermann
#
# Created:     15.01.2013
# Copyright:   (c) heistermann 2013
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python


import wradlib
import numpy as np
import pylab as pl
import glob
import os
import datetime as dt
import os

def bbox(pad, *args):
    """Get bounding box from a set of radar bin coordinates
    """
    x = np.array([])
    y = np.array([])
    for arg in args:
        x = np.append(x, arg[:,0])
        y = np.append(y, arg[:,1])
    xmin = x.min()-pad
    xmax = x.max()+pad
    ymin = y.min()-pad
    ymax = y.max()+pad

    return xmin, xmax, ymin, ymax


def plot2gmaps(x, y, data, levels, fname, cmap=pl.cm.jet):
    """
    """
    # manipulate array for plotting
    data = np.where(np.isnan(data), -9999., data)
    data = np.ma.masked_inside(data, levels[0], levels[1])
    levels = levels.copy()
    levels[0] = -10000.
    fig = pl.figure(frameon=False, figsize=(5.*get_aspectratio(x, y),5) )
##    ax = fig.add_subplot(111, aspect="equal")
    ax = pl.Axes(fig, [0., 0., 1., 1.], )
    ax.axis('off')
    fig.add_axes(ax)
    fig.patch.set_visible(False)
    cs = ax.contourf(x, y, data, levels, colors=get_colors(cmap, levels))
##    pl.savefig(fname,bbox_inches='tight', pad_inches=0, transparent=True, edgecolor="none")
    pl.savefig(fname,transparent=True, edgecolor="none")

def get_aspectratio(x, y):
    """
    """
    xmin=x.min()
    xmax=x.max()
    ymin=y.min()
    ymax=y.max()
    return (xmax-xmin)/(ymax-ymin)



def get_colors(cmap, levels, withblack=True):
    """
    """
    maxcolors = cmap.N
    ncols = len(levels)-1
    colvec = np.floor(np.linspace(0,maxcolors,ncols))
    colvec = colvec.astype("i4")
    colors = cmap(colvec)
    if withblack:
        colors[0] = np.array([0., 0., 0., 1.])
    return colors


def process_polar_level_data(datadir, radarname):
    """Reading and processing polar level data (DX) for radar <radarname>
    """
    print "Polar level processing for radar %s..." % radarname
    # preparations for loading sample data in source directory
    files = glob.glob('%s/raa*%s*bin'%(datadir,radarname))
    data  = np.empty((len(files),360,128))
    # loading the data (two hours of 5-minute images)
    for i, f in enumerate(files):
        data[i], attrs = wradlib.io.readDX(f)
    # Clutter filter on an event base
    clmap = wradlib.clutter.filter_gabella(data.mean(axis=0), tr1=12, n_p=6, tr2=1.1)
    for i, scan in enumerate(data):
        data[i] = wradlib.ipol.interpolate_polar(scan, clmap)
    # correcting for attenuation
    k = wradlib.atten.correctAttenuationHJ(data)
    data = data + k
    # converting to precipitation depth
    R = wradlib.zr.z2r(wradlib.trafo.idecibel(data), a=256, b=1.4)
    depth = wradlib.trafo.r2depth(R, 300.)
    # calculate hourly accumulation
    accum = depth.sum(axis=0)

    return accum


if __name__ == '__main__':

    # --------------------------------------------------------------------------
    # SETTINGS
    #   start and end time and interval (in secs)
    tstart   = "2008-06-02 15:00:00" # ADJUST
    tend     = "2008-06-02 15:00:00" # ADJUST
    interval = 3600
    #   levels for controu plot
    levels = np.array([0,1,2,3,5,10,15,20,25,30,35,40,45,50,60,70,80,90,100,125,150,175,200,300,400,500])
    #   data root directory
    datadir = r"P:\progress\daten\dxtest" # ADJUST
    outputdir = datadir # ADJUST
    #   PROJ.4 style projection string for target reference system
    projstr = wradlib.georef.create_projstr("gk", zone=3)
    #   set scan geometry and radar coordinates
    r               = np.arange(500.,128500.,1000.)
    az              = np.arange(0,360)
    tur_sitecoords  = (48.5861, 9.7839)
    fbg_sitecoords  = (47.8744, 8.005)
    # padding around the core bbox (in meters)
    padding = 5000.
    # --------------------------------------------------------------------------

    # compute all static composition objects only once
    #    derive projected coordinates of range-bin centroids
    #       for Tuerkheim radar
    tur_cent_lon, tur_cent_lat = wradlib.georef.polar2centroids(r, az, tur_sitecoords)
    tur_x, tur_y = wradlib.georef.project(tur_cent_lat, tur_cent_lon, projstr)
    tur_coord = np.array([tur_x.ravel(),tur_y.ravel()]).transpose()
    #       for Feldberg radar
    fbg_cent_lon, fbg_cent_lat = wradlib.georef.polar2centroids(r, az, fbg_sitecoords)
    fbg_x, fbg_y = wradlib.georef.project(fbg_cent_lat, fbg_cent_lon, projstr)
    fbg_coord = np.array([fbg_x.ravel(),fbg_y.ravel()]).transpose()

##    fig=pl.figure()
##    ax=fig.add_subplot(111, aspect="auto")
##    ax.plot(tur_x, tur_y, "r+")
##    pl.show()

    #    define target grid for composition
    xmin, xmax, ymin, ymax = bbox(padding, tur_coord, fbg_coord)
    x = np.arange(xmin,xmax+1000.,1000.)
    y = np.arange(ymin,ymax+1000.,1000.)
    grid_coords = wradlib.util.gridaspoints(x, y)

    #    derive quality information - in this case, the pulse volume
    pulse_volumes = np.tile(wradlib.qual.pulse_volume(r, 1000., 1.),360)
    #    quality grid (also static at the moment)
    tur_quality_gridded = wradlib.comp.togrid(tur_coord, grid_coords, r.max()+500., tur_coord.mean(axis=0), pulse_volumes, wradlib.ipol.Nearest)
    fbg_quality_gridded = wradlib.comp.togrid(fbg_coord, grid_coords, r.max()+500., fbg_coord.mean(axis=0), pulse_volumes, wradlib.ipol.Nearest)

    # THIS PART SHOULD ACTUALLY BE A LOOP OVER dtimes
    dtimes = wradlib.from_to(tstart, tend, interval)

    # BUT HERE'S ONLY AN EXAMPLE
    for dtime in dtimes:
        print dtime.strftime("Processing %Y-%m-%d %H...")
        # processing polar level radar data
        # (NEED TO ADAPT process_polar_level_data TO UNPACK THE MATCHING DATA FOR dtime FROM datadir)
        #   Tuerkheim
        tur_accum = process_polar_level_data(datadir, "tur")
        #   Feldberg
        fbg_accum = process_polar_level_data(datadir, "fbg")
        # gridding the data
        tur_gridded = wradlib.comp.togrid(tur_coord, grid_coords, r.max()+500., tur_coord.mean(axis=0), tur_accum.ravel(), wradlib.ipol.Nearest)
        fbg_gridded = wradlib.comp.togrid(fbg_coord, grid_coords, r.max()+500., fbg_coord.mean(axis=0), fbg_accum.ravel(), wradlib.ipol.Nearest)
        # compose the both radar-data based on the quality information calculated above
        composite = wradlib.comp.compose_weighted([tur_gridded, fbg_gridded],[1./(tur_quality_gridded+0.001),1./(fbg_quality_gridded+0.001)])
        # Save the data as hdf5
        metadata = {} # ADD METADATA (e.g. dtime, xy coordinates, projection etc)
        retval = wradlib.io.to_hdf5(os.path.join(outputdir, dtime.strftime("turfbg_comp_%Y%m%d%H%M%S-1h.h5")), composite, metadata=metadata)
        # Plotting Google Maps compatible image
        plot2gmaps(x, y, composite.reshape((len(x),len(y)), order="F").transpose(), levels, os.path.join(outputdir, dtime.strftime("turfbg_comp_%Y%m%d%H%M%S-1h.png")))
        ##wradlib.vis.cartesian_plot(composite.reshape((len(x),len(y))), x=x, y=y, unit="mm", colormap="spectral", classes=levels)

    [lllon, urlon], [lllat, urlat] = wradlib.georef.project([ymin, ymax], [xmin, xmax], projstr=projstr, inverse=True)
    print lllon, urlon, lllat, urlat