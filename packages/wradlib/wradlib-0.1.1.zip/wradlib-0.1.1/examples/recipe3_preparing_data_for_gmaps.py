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


def get_colors(cmap, levels):
    """
    """
    maxcolors = cmap.N
    ncols = len(levels)-1
    colvec = np.floor(np.linspace(0,maxcolors,ncols))
    colvec = colvec.astype("i4")
    return cmap(colvec)



if __name__ == '__main__':

    testdata = np.loadtxt('data/polar_R_tur.gz')
    classes = np.arange(0,35)
#    testdata = np.ma.masked_less(testdata, 0.5)
#    wradlib.vis.polar_plot(testdata, title='Reflectivity', unit='dBZ', colormap='spectral', classes=classes, extend='max')

    # set scan geometry and radar coordinates
    r               = np.arange(500.,128500.,1000.)
    az              = np.arange(0,360)
    tur_sitecoords  = (48.5861, 9.7839)
    fbg_sitecoords  = (47.8744, 8.005)

    # PROJ.4 style projection string for target reference system
    projstr = wradlib.georef.create_projstr("gk",zone=3)

    # derive Gauss-Krueger Zone 3 coordinates of range-bin centroids
    #   for Tuerkheim radar
    tur_cent_lon, tur_cent_lat = wradlib.georef.polar2centroids(r, az, tur_sitecoords)
    tur_x, tur_y = wradlib.georef.project(tur_cent_lat, tur_cent_lon, projstr)
    tur_coord = np.array([tur_x.ravel(),tur_y.ravel()]).transpose()

    # define target grid for composition
    xmin, xmax, ymin, ymax = bbox(10000., tur_coord)
    x = np.linspace(xmin,xmax,1000.)
    y = np.linspace(ymin,ymax,1000.)
    grid_coords = wradlib.util.gridaspoints(x, y)

    gridded = wradlib.comp.togrid(tur_coord, grid_coords, r.max()+500., tur_coord.mean(axis=0), testdata.ravel(), wradlib.ipol.Nearest)
#    gridded = np.ma.masked_invalid(gridded)
    gridded = np.where(np.isnan(gridded), -9999, gridded)
    gridded = np.ma.masked_inside(gridded, 0., 1.)


    fig = pl.figure(frameon=False)
    ax = fig.add_subplot(111)
    ax.axis('off')
    fig.patch.set_visible(False)
#    ax.imshow(gridded.reshape((len(x),len(y))), origin="lower", colormap="spectral")
    levels=[-10000,1,2,4,6,8,10,12,14,16,18,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,110,120,130,140,150,160,170,180,190,200,300]
    ax.contourf(x, y, gridded.reshape((len(x),len(y))), levels=levels, colors=get_colors(pl.cm.spectral, levels))
    pl.savefig('output.png',bbox_inches='tight', pad_inches=0, transparent=True, edgecolor="none")
    pl.show()
##    wradlib.vis.cartesian_plot(gridded.reshape((len(x),len(y))), x=x, y=y, unit="mm", colormap="spectral", classes=classes)
