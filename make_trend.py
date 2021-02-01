#!/bin/env python3
import gdal
import numpy as np
import os
import sys
import glob
import subprocess
import datetime

tileid = sys.argv[1]

files = glob.glob(tileid + '_*_zscore_base_3weekavg.tif')
files.sort()
print("First file: %s" % (files[0]))
print("Last file: %s" % (files[-1]))

numfiles = len(files)
print("Total file: %d" % (numfiles))

dslist = []
tDS = gdal.Open(files[0], gdal.GA_ReadOnly)
xsize = tDS.RasterXSize
ysize = tDS.RasterYSize
gt = tDS.GetGeoTransform()
proj = tDS.GetProjection()
outfile = tileid + '_zscore_trend.tif'
drv  = gdal.GetDriverByName('GTiff')
outDS = drv.Create(outfile, xsize, ysize, 1, eType=gdal.GDT_Float32, options=['COMPRESS=LZW', 'TILED=YES'])
outDS.SetGeoTransform(gt)
outDS.SetProjection(proj)
outDS.GetRasterBand(1).SetNoDataValue(-9999.)
tDS = None

maskfile = 'CoralNew/' + tileid + '_coral.tif'                                  
if os.path.exists(maskfile):                                                    
  print('Maskfile %s' % (maskfile))                                             
  maskset = gdal.Open(maskfile, gdal.GA_ReadOnly)

for j in range(numfiles):
  tmpDS = gdal.Open(files[j], gdal.GA_ReadOnly)
  dslist.append(tmpDS)

for _line in range(ysize):
  alllines = np.zeros((xsize, numfiles))
  for k,ds in enumerate(dslist):
    alllines[:,k] = np.squeeze(ds.GetRasterBand(1).ReadAsArray(0, _line, xsize, 1))
  bad = np.equal(alllines, -9999.) 
  allbad = np.all(np.equal(alllines, -9999.), axis=1)
  alllines[bad] = 0.0
  newtrend = np.zeros(xsize)
  for b in range(numfiles-1, 0, -1):
    newtrend += alllines[:,b] - alllines[:,(b-1)]
  newtrend[allbad] = -9999.    

  if (os.path.exists(maskfile)):
    mask = np.squeeze(maskset.GetRasterBand(1).ReadAsArray(0, _line, xsize,1))              
  else:                                                                       
    mask = np.ones((xsize)).astype(np.uint8)
  newtrend[mask == 0] = -9999.
  outDS.GetRasterBand(1).WriteArray(newtrend.reshape(1, xsize), 0, _line)

for thisDS in dslist:
  thisDS = None
if (os.path.exists(maskfile)):
  maskset = None

outBand = None
outDS = None

subprocess.call('gdaladdo {} 2 4 8 16 32 64 128'.format(outfile),shell=True)

