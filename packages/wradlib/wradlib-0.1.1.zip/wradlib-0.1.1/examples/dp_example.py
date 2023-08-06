#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      heistermann
#
# Created:     20/12/2013
# Copyright:   (c) heistermann 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import wradlib
import numpy as np
import pylab as pl

pl.interactive(True)

kdp_true   = np.abs(np.sin(1*np.arange(0,10,0.1)))
phidp_true = 2*np.cumsum(kdp_true)
phidp_raw  = phidp_true# + np.random.uniform(-1,1,len(phidp_true))
gaps       = np.concatenate([ range(10,20),range(30,40),range(60,80) ])
phidp_raw[gaps] = np.nan

phidp_raw = phidp_raw.reshape((1,-1))
phidp_fill = phidp_raw.copy()
phidp_fill = wradlib.dp._fill_sweep(phidp_fill, kind="cubic")

pl.plot(phidp_fill[0], "b-")
pl.plot(phidp_raw[0], "r-")
pl.show()

kdp_fd = wradlib.dp.kdp_from_phidp_finitediff(phidp_raw)
kdp_lr = wradlib.dp.kdp_from_phidp_linregress(phidp_raw)
kdp_so = wradlib.dp.kdp_from_phidp_sobel(phidp_raw)
kdp_cv = wradlib.dp.kdp_from_phidp_convolution(phidp_raw)

#pl.plot(np.ma.masked_invalid(phidp_true), "b--", label="phidp_true")
#pl.plot(np.ma.masked_invalid(phidp_raw), "b-", label="phidp_raw")
pl.plot(kdp_true, "g-", label="kdp_true")
pl.plot(np.ma.masked_invalid(kdp_fd), "r-", label="kdp_df")
pl.plot(np.ma.masked_invalid(kdp_lr), "b-", label="kdp_lr")
pl.plot(np.ma.masked_invalid(kdp_so), "rd", label="kdp_so")
pl.plot(np.ma.masked_invalid(kdp_cv), "k+", label="kdp_cv")
pl.legend(("kdp_true", "kdp_fd", "kdp_lr", "kdp_so", "kdp_cv"))

