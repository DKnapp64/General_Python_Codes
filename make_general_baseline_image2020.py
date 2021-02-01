#!/bin/env python3
import gdal
import numpy as np
import os, sys
import glob
import warnings

if (len(sys.argv) != 2):
  print('make_general_baseline_image2020.py ascdesc/tileid')
  print('where:')
  print('tileid = the tileid of the tile with ascdesc, e.g., descending/L15-0172E-0922N')
  print('')
  sys.exit(0)

splitvals = sys.argv[1].split('/')
tile = splitvals[1]
ascdesc = splitvals[0]

## Spratly Islands
blweeks = ['20191202_to_20191209', '20191209_to_20191216', 
'20191216_to_20191223', '20191223_to_20191230', 
'20191230_to_20200106', '20200106_to_20200113', 
'20200113_to_20200120', '20200120_to_20200127', 
'20200127_to_20200203', '20200203_to_20200210', 
'20200210_to_20200217', '20200217_to_20200224', 
'20200224_to_20200302', '20200302_to_20200309', 
'20200309_to_20200316', '20200316_to_20200323', 
'20200323_to_20200330'] 

drv = gdal.GetDriverByName('GTiff')

dslist = []
baseimg = np.zeros((4096,4096,2)) - 9999
## open the data sets for this group
for k,theweek in enumerate(blweeks):
  rbtile = theweek + '/' + ascdesc + '/' + tile + '_br_comp.tif'
  if not os.path.exists(rbtile):
    rbtile2 = theweek + '/' + ascdesc + '/' + tile + '_br_comp_masked.tif'
    if os.path.exists(rbtile2):
      rbtile = rbtile2
    else:
      continue
  dslist.append(gdal.Open(rbtile, gdal.GA_ReadOnly))
      
if (len(dslist) < 2):
  print('Not enough data (only %d) for %s for tile %s' % (len(dslist), ascdesc, tile))
  for j in dslist:
    j = None
  sys.exit(0)

gt = dslist[0].GetGeoTransform()
proj = dslist[0].GetProjection()
outtile = 'BaseFiles2020/' + tile + '_base.tif'
outDS = drv.Create(outtile, 4096, 4096, 5, eType=gdal.GDT_Float32, \
  options=['COMPRESS=LZW', 'TILED=YES'])
outDS.SetGeoTransform(gt)
outDS.SetProjection(proj)
Band1 = outDS.GetRasterBand(1)
Band2 = outDS.GetRasterBand(2)
Band3 = outDS.GetRasterBand(3)
Band4 = outDS.GetRasterBand(4)
Band5 = outDS.GetRasterBand(5)

layerstack = []

for w,thisDS in enumerate(dslist):
  layerstack.append(thisDS.GetRasterBand(1))
  ## print('Date %d  Min: %f  Max:%f' % (w, np.min(temp), np.max(temp)))

for j in range(dslist[0].RasterYSize):
  lines = np.zeros((len(dslist), dslist[0].RasterXSize))
  for w,thisBand in enumerate(layerstack):
    lines[w,:] = thisBand.ReadAsArray(0, j, dslist[w].RasterXSize, 1)
    bad = np.logical_or(np.logical_not(np.isfinite(lines)), np.equal(lines, -9999))
    lines[bad] = np.nan
    # I expect to see RuntimeWarnings in this block
    # There very well may be empty slices here (i.e., all Nans).  Suppress those warnings.
    with warnings.catch_warnings():
      warnings.simplefilter("ignore", category=RuntimeWarning)
      meanval = np.nanmean(lines, axis=0).reshape(1, dslist[0].RasterXSize) 
      sdev = np.nanstd(lines, axis=0).reshape(1, dslist[0].RasterXSize)
      minval = np.nanmin(lines, axis=0).reshape(1, dslist[0].RasterXSize)
      maxval = np.nanmax(lines, axis=0).reshape(1, dslist[0].RasterXSize)
      medianval = np.nanmedian(lines, axis=0).reshape(1, dslist[0].RasterXSize)
      
  findex = np.logical_not(np.isfinite(meanval))
  meanval[findex] = -9999.0
  sdev[findex] = -9999.0
  minval[findex] = -9999.0
  maxval[findex] = -9999.0
  medianval[findex] = -9999.0
  Band1.WriteArray(meanval.astype(np.float32), 0, j)
  Band2.WriteArray(sdev.astype(np.float32), 0, j)
  Band3.WriteArray(minval.astype(np.float32), 0, j)
  Band4.WriteArray(maxval.astype(np.float32), 0, j)
  Band5.WriteArray(medianval.astype(np.float32), 0, j)

Band1.SetNoDataValue(-9999)
Band2.SetNoDataValue(-9999)
Band3.SetNoDataValue(-9999)
Band4.SetNoDataValue(-9999)
Band5.SetNoDataValue(-9999)

## all done.  close everything up
outDS = None
for k in dslist:
  k = None
