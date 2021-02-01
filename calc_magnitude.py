#!/bin/env python3
import argparse
import gdal
import numpy as np
import pandas as pd
import os
import sys
import yaml
from tqdm import tqdm
import glob
import subprocess
import datetime

tileid = sys.argv[1]
ascdesc = sys.argv[2]
stopat = sys.argv[3]

thedirs = glob.glob(ascdesc + '_20[0-9][0-9][0-1][0-9][0-3][0-9]_to_20[0-9][0-9][0-1][0-9][0-3][0-9]')
files = []

for thedir in thedirs:
  tilepath = thedir + os.path.sep + tileid + '_br_comp.tif'
  if os.path.exists(tilepath):
    files.append(tilepath)

files.sort()
print("Got %d files for tile %s" % (len(files), tileid))
print("First file: %s" % (files[0]))
print("Last file: %s" % (files[-1]))

baseline_files = [x for x in files if '201908' not in x and '201909' not in x and '201910' not in x and '201911' not in x]
temp_bleaching_files = [x for x in files if '201908' in x or '201909' in x or '201910' in x or '201911' in x]
bleaching_files = []

stopdate = datetime.datetime(int(stopat[-8:-4]), int(stopat[-4:-2]), int(stopat[-2:])) + datetime.timedelta(days=1)

for j,name in enumerate(temp_bleaching_files):
  imgdatestr = name.split('_')[3][0:8]
  imgdate = datetime.datetime(int(imgdatestr[0:4]), int(imgdatestr[4:6]), int(imgdatestr[6:]))
  if (imgdate < stopdate):
    bleaching_files.append(name) 

if (len(bleaching_files) < 2):
  print('Not enough times series tiles to do differencing.  Exiting.')
  sys.exit(0)

datasets = []
for _f in range(len(baseline_files)):
    datasets.append(gdal.Open(baseline_files[_f],gdal.GA_ReadOnly))
    print((baseline_files[_f],datasets[-1].RasterXSize,datasets[-1].RasterYSize))

bleaching_datasets = []
for _f in range(len(bleaching_files)):
    bleaching_datasets.append(gdal.Open(bleaching_files[_f],gdal.GA_ReadOnly))
    print((bleaching_files[_f],bleaching_datasets[-1].RasterXSize,bleaching_datasets[-1].RasterYSize))

maskfile = 'CoralTiles10m/' + tileid + '_coral.tif'
print('Maskfile %s' % (maskfile))
maskset = gdal.Open(maskfile, gdal.GA_ReadOnly)

driver = gdal.GetDriverByName('GTiff')
driver.Register()

x_off = 0
y_off = 0
x_size = datasets[0].RasterXSize
y_size = datasets[0].RasterYSize

trans = datasets[0].GetGeoTransform()
out_trans = list(trans)
out_trans[0] += x_off*trans[1]
out_trans[3] += y_off*trans[5]

## outname = 'persistant_deviation_{}_{}_{:0>2d}.tif'.format(ascdesc, tileid, stopat)
outname = 'magnitude_{}_{}_{}.tif'.format(ascdesc, tileid, stopdate.strftime('%Y%m%d'))
outDataset = driver.Create(outname,x_size,y_size,1,gdal.GDT_Float32,options=['COMPRESS=LZW','TILED=YES'])
outDataset.SetProjection(datasets[0].GetProjection())
outDataset.SetGeoTransform(out_trans)

magnitude = np.zeros((y_size,x_size), dtype=np.float32) - 9999

for _line in range(y_off, y_off+y_size):

    # get the baseline values
    line_dat = np.zeros((x_size,len(datasets)))
    for _f in range(len(baseline_files)):
        line_dat[:,_f] = np.squeeze(datasets[_f].ReadAsArray(x_off,_line,x_size,1))

    # merge those values together to determine baseline
    line_dat[line_dat == -9999] = np.nan
    baseline = np.nanmax(line_dat,axis=1)
    nanindex = np.logical_not(np.isfinite(baseline))
    baseline[nanindex] = -9999

    # step through bleaching datasets
    n_dev = np.zeros(x_size)
    max_dev = np.zeros(x_size) - 9999
    templist = []
    for _f in range(len(bleaching_datasets)):
        ldat = np.squeeze(bleaching_datasets[_f].ReadAsArray(x_off,_line,x_size,1))
        # add one for each deviation above baseline
        n_dev[ldat > baseline] += 1

        # save the maximum deviation
        max_dev[ldat > baseline] = np.maximum(ldat - baseline, max_dev)[ldat > baseline]
        ## max_dev[ldat > baseline] = np.median(ldat - baseline, max_dev)[ldat > baseline]
        templist.append(max_dev)
        
    mask = np.squeeze(maskset.ReadAsArray(x_off,_line,x_size,1))

    n_dev[mask == 0] = -9999
    max_dev[mask == 0] = -9999
    nanindex = np.logical_not(np.isfinite(max_dev))
    max_dev[nanindex] = -9999

    tempstack = np.stack(templist)
    tempnan = np.logical_or(np.equal(tempstack, -9999), np.logical_not(np.isfinite(tempstack)))
    tempstack[tempnan] = np.nan
    maxdev_median = np.nanmedian(tempstack, axis=0)
    missing = np.logical_not(np.isfinite(maxdev_median))
    maxdev_median[missing] = -9999
    good = np.logical_and(np.not_equal(maxdev_median, -9999), np.not_equal(baseline, -9999))
    magnitude[_line-y_off,good] = maxdev_median[good]/baseline[good]
    nanindex = np.logical_not(np.isfinite(magnitude))
    magnitude[nanindex] = -9999

outDataset.GetRasterBand(1).WriteArray(magnitude)
outDataset.GetRasterBand(1).SetNoDataValue(-9999)
del outDataset

for thisDS in bleaching_datasets:
  thisDS = None

for thisDS in datasets:
  thisDS = None

## print(np.histogram(change_dat[change_dat != -9999]))
subprocess.call('gdaladdo {} 2 4 8 16 32 64 128'.format(outname),shell=True)

