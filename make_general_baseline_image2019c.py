#!/bin/env python3
import gdal
import numpy as np
import os, sys
import glob
import warnings

if (len(sys.argv) != 2):
  print('make_general_baseline_image2019c.py ascdesc/tileid')
  print('where:')
  print('tileid = the tileid of the tile with ascdesc, e.g., descending/L15-0172E-0922N')
  print('')
  sys.exit(0)

## splitvals = sys.argv[1].split('/')
## tile = splitvals[1]
## ascdesc = splitvals[0]
tile = sys.argv[1]

## for GBR
blweeks = ['20190930_to_20191007', '20191007_to_20191014', 
'20191014_to_20191021', '20191021_to_20191028', 
'20191028_to_20191104', '20191104_to_20191111',
'20191111_to_20191118', '20191118_to_20191125',
'20191125_to_20191202', '20191202_to_20191209',
'20191209_to_20191216', '20191216_to_20191223',
'20191223_to_20191230']

blweeks2 = ['20191230_to_20200106', '20200106_to_20200113',
'20200113_to_20200120', '20200120_to_20200127',
'20200127_to_20200203', '20200203_to_20200210',
'20200210_to_20200217', '20200217_to_20200224',
'20200224_to_20200302', '20200302_to_20200309',
'20200309_to_20200316', '20200316_to_20200323',
'20200323_to_20200330', '20200330_to_20200406',
'20200406_to_20200413', '20200413_to_20200420']

## for Moorea
## blweeks = ['20181231_to_20190107', '20190107_to_20190114', 
## '20190114_to_20190121', '20190121_to_20190128', 
## '20190128_to_20190204', '20190204_to_20190211', 
## '20190211_to_20190218', '20190218_to_20190225', 
## '20190225_to_20190304', '20190304_to_20190311', 
## '20190311_to_20190318', '20190318_to_20190325'] 

## Spratly Islands
## blweeks = ['20191202_to_20191209', '20191209_to_20191216', 
## '20191216_to_20191223', '20191223_to_20191230', 
## '20191230_to_20200106', '20200106_to_20200113', 
## '20200113_to_20200120', '20200120_to_20200127', 
## '20200127_to_20200203', '20200203_to_20200210', 
## '20200210_to_20200217', '20200217_to_20200224', 
## '20200224_to_20200302', '20200302_to_20200309', 
## '20200309_to_20200316', '20200316_to_20200323', 
## '20200323_to_20200330'] 

## for Hawaii 2019
## blweeks = ['20190429_to_20190506', '20190506_to_20190513', 
##            '20190513_to_20190520', '20190520_to_20190527', 
##            '20190527_to_20190603', '20190603_to_20190610', 
##            '20190610_to_20190617', '20190617_to_20190624', 
##            '20190624_to_20190701', '20190701_to_20190708', 
##            '20190708_to_20190715', '20190715_to_20190722', 
##            '20190722_to_20190729']

## blweeks2 = ['20190729_to_20190805', '20190805_to_20190812', 
## '20190812_to_20190819', '20190819_to_20190826', 
## '20190826_to_20190902', '20190902_to_20190909', 
## '20190909_to_20190916', '20190916_to_20190923', 
## '20190923_to_20190930', '20190930_to_20191007', 
## '20191007_to_20191014', '20191014_to_20191021', 
## '20191021_to_20191028', '20191028_to_20191104']

## for Hawaii 2020
## blweeks = ['20200406_to_20200413', '20200413_to_20200420', 
##            '20200420_to_20200427', '20200427_to_20200504', 
##            '20200504_to_20200511', '20200511_to_20200518', 
##            '20200518_to_20200525', '20200525_to_20200601', 
##            '20200601_to_20200608', '20200608_to_20200615', 
##            '20200615_to_20200622', '20200622_to_20200629']

drv = gdal.GetDriverByName('GTiff')
dslist = []

for t,temp in enumerate(blweeks):
  ## open the data sets for this group
  ## rbtile = temp + '/' + ascdesc + '/' + tile + '_rb_comp.tif'
  rbtile = temp + '/' + tile + '_rb_comp.tif'
  if not os.path.exists(rbtile):
    ## rbtile2 = temp + '/' + ascdesc + '/' + tile + '_rb_comp_masked.tif'
    rbtile2 = temp + '/' + tile + '_rb_comp_masked.tif'
    if os.path.exists(rbtile2):
      rbtile = rbtile2
    else:
      continue
  dslist.append(gdal.Open(rbtile, gdal.GA_ReadOnly))
 
if (len(dslist) < 2):
  print('Not enough data (only %d) for %s for tile %s' % (len(dslist), tile))
  for j in dslist:
    j = None
  sys.exit(0)

gt = dslist[0].GetGeoTransform()
proj = dslist[0].GetProjection()
outtile = 'JiweiMethod/' + tile + '_base.tif'
outDS = drv.Create(outtile, 4096, 4096, 1, eType=gdal.GDT_Float32, \
  options=['COMPRESS=LZW', 'TILED=YES'])
outDS.SetGeoTransform(gt)
outDS.SetProjection(proj)
Band1 = outDS.GetRasterBand(1)

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
      
  findex = np.logical_not(np.isfinite(meanval))
  meanval[findex] = -9999.0
  Band1.WriteArray(meanval.astype(np.float32), 0, j)

Band1.SetNoDataValue(-9999)

## all done.  close everything up
outDS = None
for k in dslist:
  k = None

