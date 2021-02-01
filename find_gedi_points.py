#!/usr/bin/env python3
import h5py
import pandas as pd
import numpy as np
import geopandas as gpd
import os, sys
import time
import glob

outfile = 'gedi_point_report2.txt'
fout = open(outfile, 'w')
infiles = glob.glob('PEC/GEDI02_B*.h5')
## print(list(f.keys()))
## print("File: %s" % (fname))

infiles = infiles[133:]

for fname in infiles:
    print(fname)
    f = h5py.File(fname, 'r')
    groups = [t for t in f.keys()]
    for group in groups:
        if (group == 'METADATA'):
            continue
        latitude_bin0 = f[group]['geolocation']['latitude_bin0']
        longitude_bin0 = f[group]['geolocation']['longitude_bin0']
        ## isqual = np.logical_and(np.equal(l2a_quality_flag, 1), np.equal(l2b_quality_flag, 1))
        valid_x = np.isfinite(longitude_bin0)
        valid_y = np.isfinite(latitude_bin0)
        within_x = np.logical_and(np.greater(longitude_bin0,-76.04), np.less(longitude_bin0,-74.93))
        within_y = np.logical_and(np.greater(latitude_bin0,-7.5), np.less(latitude_bin0,-7.29))
        goodstack = np.stack((valid_x, valid_y, within_x, within_y))
        good = np.all(goodstack, axis=0)
        fout.write('%s, %s, %d\n' % (fname, group, np.sum(good)))

    f.close()

fout.close()

