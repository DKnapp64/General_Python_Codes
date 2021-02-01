#!/bin/env python3
import gdal
import numpy as np
import os, sys
import datetime

rbmosfiles = ['rb_mosaic_20190805_to_20190812_basediff.tif', 
'rb_mosaic_20190812_to_20190819_basediff.tif', 
'rb_mosaic_20190819_to_20190826_basediff.tif', 
'rb_mosaic_20190826_to_20190902_basediff.tif', 
'rb_mosaic_20190902_to_20190909_basediff.tif', 
'rb_mosaic_20190909_to_20190916_basediff.tif', 
'rb_mosaic_20190916_to_20190923_basediff.tif', 
'rb_mosaic_20190923_to_20190930_basediff.tif', 
'rb_mosaic_20190930_to_20191007_basediff.tif', 
'rb_mosaic_20191007_to_20191014_basediff.tif', 
'rb_mosaic_20191014_to_20191021_basediff.tif', 
'rb_mosaic_20191021_to_20191028_basediff.tif', 
'rb_mosaic_20191028_to_20191104_basediff.tif', 
'rb_mosaic_20191104_to_20191111_basediff.tif', 
'rb_mosaic_20191111_to_20191118_basediff.tif']

##-rw-rw-r-- 1 dknapp4 dknapp4 11274289280 Nov 25 21:51 baseon.npy
##-rw-rw-r-- 1 dknapp4 dknapp4 11274289280 Nov 25 21:54 coralmaskon.npy
##-rw-rw-r-- 1 dknapp4 dknapp4 11274289280 Nov 25 21:56 rbon.npy
##-rw-rw-r-- 1 dknapp4 dknapp4 11274289280 Nov 25 22:10 persdevon.npy
##-rw-rw-r-- 1 dknapp4 dknapp4 11274289280 Nov 25 22:20 allstuff.npy

basefile = 'baseline_rb.tif'
## coralfile = 'CoralNew/coral_mask_mosaic.tif'
pdev = 'persdev_mosaic_20191119.tif'

bDS = gdal.Open(basefile, gdal.GA_ReadOnly)
basedata = bDS.GetRasterBand(1).ReadAsArray()
bDS = None

pDS = gdal.Open(pdev, gdal.GA_ReadOnly)
gt = pDS.GetGeoTransform()
proj = pDS.GetProjection()
pdata = pDS.GetRasterBand(1).ReadAsArray()

pDS = None
allstuff = np.load('allstuff.npy', mmap_mode='r')
vals = [2,3,4,5,6,7,8,9,10,11,12,13,14,15]
## vals = vals[11:]

for k,uval in enumerate(vals):
  thisval = np.equal(pdata, uval)
  allstuffval = np.logical_and(thisval, allstuff)
  index = np.nonzero(allstuffval)
  numpix = np.sum(allstuffval)
  del allstuffval
  print('Started Working on PV %d with %d pixels' % (uval, numpix))
  if (numpix >= 2000):
    randabove = np.random.randint(low=0, high=numpix, size=2000)
    rows = index[0][randabove]
    cols = index[1][randabove]
  else:
    rows = index[0]
    cols = index[1]
  np.save('randomsample_row_num%02d_20191127.npy' % (uval), rows)
  np.save('randomsample_col_num%02d_20191127.npy' % (uval), cols)
  basesamp = basedata[rows, cols]
  np.save('basesamp_num%02d.npy' % (uval), basesamp)
  
  for j,rbname in enumerate(rbmosfiles):
  
    tempdate = (os.path.splitext(os.path.basename(rbname))[0]).split('_')[4]
    thedate = (datetime.date(int(tempdate[0:4]), int(tempdate[4:6]), int(tempdate[6:8])) + datetime.timedelta(days=1)).strftime('%Y%m%d')

    rbDS = gdal.Open(rbname, gdal.GA_ReadOnly)
    rbdata = rbDS.GetRasterBand(1).ReadAsArray()
    rbsamp = rbdata[rows, cols]
    np.save('rbsamp_%s_num%02d.npy' % (thedate,uval), rbsamp)
    del rbdata
    rbDS = None
    print('Finished Val %d for %s' % (uval, thedate))


