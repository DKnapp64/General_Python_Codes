#!/bin/env python3
import gdal
import numpy as np
import os
import sys
import yaml
import glob
import datetime

tileid = sys.argv[1]
ascdesc = sys.argv[2]

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

datasets = []
for _f in range(len(baseline_files)):
    datasets.append(gdal.Open(baseline_files[_f],gdal.GA_ReadOnly))
    print((baseline_files[_f],datasets[-1].RasterXSize,datasets[-1].RasterYSize))

driver = gdal.GetDriverByName('GTiff')
driver.Register()

x_off = 0
y_off = 0
x_size = datasets[0].RasterXSize
y_size = datasets[0].RasterYSize
## print('XSize: %d   YSize: %d' % (x_size, y_size))

trans = datasets[0].GetGeoTransform()
out_trans = list(trans)
out_trans[0] += x_off*trans[1]
out_trans[3] += y_off*trans[5]

outname = 'baseline_{}_{}.tif'.format(ascdesc, tileid)
outDataset = driver.Create(outname,x_size,y_size,1,gdal.GDT_Float32,options=['COMPRESS=LZW','TILED=YES'])
outDataset.SetProjection(datasets[0].GetProjection())
outDataset.SetGeoTransform(out_trans)

baseline = np.zeros((y_size,x_size),dtype=np.float32) - 9999

for _line in range(y_off, y_off+y_size):

  # get the baseline values
  line_dat = np.zeros((x_size,len(datasets)))
  for _f in range(len(baseline_files)):
    line_dat[:,_f] = np.squeeze(datasets[_f].ReadAsArray(x_off,_line,x_size,1))

  # merge those values together to determine baseline
  line_dat[line_dat == -9999] = np.nan
  baseline = np.nanmax(line_dat,axis=1)
  baseline[baseline == np.nan] = -9999
  outDataset.GetRasterBand(1).WriteArray(np.expand_dims(baseline,axis=0),0,_line)

outDataset.GetRasterBand(1).SetNoDataValue(-9999)
del outDataset

for thisDS in datasets:
  thisDS = None


