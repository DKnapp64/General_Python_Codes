#!/bin/env python3
import gdal
import numpy as np
import os, sys
import yaml
import glob
import datetime

rbmosfiles = ['rb_mosaic_20190805_to_20190812.tif', 
'rb_mosaic_20190812_to_20190819.tif', 
'rb_mosaic_20190819_to_20190826.tif', 
'rb_mosaic_20190826_to_20190902.tif', 
'rb_mosaic_20190902_to_20190909.tif', 
'rb_mosaic_20190909_to_20190916.tif', 
'rb_mosaic_20190916_to_20190923.tif', 
'rb_mosaic_20190923_to_20190930.tif', 
'rb_mosaic_20190930_to_20191007.tif', 
'rb_mosaic_20191007_to_20191014.tif', 
'rb_mosaic_20191014_to_20191021.tif', 
'rb_mosaic_20191021_to_20191028.tif', 
'rb_mosaic_20191028_to_20191104.tif', 
'rb_mosaic_20191104_to_20191111.tif', 
'rb_mosaic_20191111_to_20191118.tif']

persdevfiles = ['persdev_mosaic_20190813.tif', 'persdev_mosaic_20190820.tif'
'persdev_mosaic_20190827.tif', 'persdev_mosaic_20190903.tif', 
'persdev_mosaic_20190910.tif', 'persdev_mosaic_20190917.tif', 
'persdev_mosaic_20190924.tif', 'persdev_mosaic_20191001.tif', 
'persdev_mosaic_20191008.tif', 'persdev_mosaic_20191015.tif', 
'persdev_mosaic_20191022.tif', 'persdev_mosaic_20191029.tif', 
'persdev_mosaic_20191105.tif', 'persdev_mosaic_20191112.tif', 
'persdev_mosaic_20191119.tif']

basefile = 'baseline_rb.tif'
coralfile = 'CoralNew/coral_mask_mosaic.tif'

coralDS = gdal.Open(coralfile, gdal.GA_ReadOnly)
baseDS = gdal.Open(basefile, gdal.GA_ReadOnly)
cgt = coralDS.GetGeoTransform()
bgt = baseDS.GetGeoTransform()

if not np.allclose(cgt, bgt, atol=0.001):
  print('Coral and Baseline images do not match Geospatially..exiting')
  coralDS, baseDS = None, None
  sys.exit(0)

if (coralDS.RasterXSize != baseDS.RasterXSize) or (coralDS.RasterYSize != baseDS.RasterYSize):
  print('Coral and Baseline images do not have the same dimensions..exiting')
  coralDS, baseDS = None, None
  sys.exit(0)
  
coralmask = coralDS.GetRasterBand(1).ReadAsArray()
basedata = baseDS.GetRasterBand(1).ReadAsArray()
coralmaskon = np.equal(coralmask, 1)
basedataon = np.logical_and(np.not_equal(basedata, -9999), np.not_equal(basedata, 0))
del coralmask
np.save('coralmaskon.npy', coralmaskon)
np.save('basedataon.npy', basedataon)

for j,rbname in enumerate(rbmosfiles):
  thedate = os.path.splitext(os.path.basename(persdevfiles[j]))[0][-8:]

  print('Started Working on %s' % (thedate))

  rbDS = gdal.Open(rbname, gdal.GA_ReadOnly)
  rgt = rbDS.GetGeoTransform()
  if not np.allclose(cgt, rgt, atol=0.001):
    print('This image %s does not match Geospatially..exiting' % (os.path.basename(rbname)))
    coralDS, baseDS, rbDS = None, None, None
    sys.exit(0)
     
  if (coralDS.RasterXSize != rbDS.RasterXSize) or (coralDS.RasterYSize != rbDS.RasterYSize):
    print('This image %s does not have same dimensions..exiting' % (os.path.basename(rbname)))
    coralDS, baseDS, rbDS = None, None, None
    sys.exit(0)

  rbdata = rbDS.GetRasterBand(1).ReadAsArray()
  rbon = np.logical_and(np.not_equal(rbdata, -9999), np.not_equal(rbdata, 0))
  np.save('rbon_'+thedate+'.npy', rbon)                                         
  
  pDS = gdal.Open(persdevfiles[j], gdal.GA_ReadOnly)
  pdata = pDS.GetRasterBand(1).ReadAsArray()
  above = np.greater_equal(pdata, 2)
  np.save('above_'+thedate+'.npy', above)                                       
  below = np.less(pdata, 2)
  np.save('below_'+thedate+'.npy', below)                                       
  allgood = np.all(np.dstack((coralmaskon, basedataon, rbon)), axis=-1)
  np.save('allgood_'+thedate+'.npy', allgood)                                   

  print('Stacked Coralmask, Baseline, and Rb')
  gabove = np.logical_and(above, allgood)
  gbelow = np.logical_and(below, allgood)
  del allgood
  numabove = np.sum(gabove)
  numbelow = np.sum(gbelow)
  print('%s: Above: %d    Below: %d' % (rbname, numabove, numbelow))
  np.save('gbelow_'+thedate+'.npy', gbelow)                                       
  np.save('gabove_'+thedate+'.npy', gabove)                                       
  indexabove = np.nonzero(gabove)
  indexbelow = np.nonzero(gbelow)
  del gabove
  del gbelow
  randabove = np.random.randint(low=0, high=numabove, size=20000)
  randbelow = np.random.randint(low=0, high=numbelow, size=20000)
  pabove = pdata[indexabove[0][randabove], indexabove[1][randabove]]
  pbelow = pdata[indexbelow[0][randbelow], indexbelow[1][randbelow]]
  rabove = rbdata[indexabove[0][randabove], indexabove[1][randabove]]
  rbelow = rbdata[indexbelow[0][randbelow], indexbelow[1][randbelow]]
  baseabove = basedata[indexabove[0][randabove], indexabove[1][randabove]]
  basebelow = basedata[indexbelow[0][randbelow], indexbelow[1][randbelow]]
  outfile = 'rb_baseline_bleach_data_'+thedate+'.npz'
  np.savez(outfile, pabove=pabove, pbelow=pbelow, rabove=rabove, rbelow=rbelow, 
    baseabove=baseabove, basebelow=basebelow)
  rbDS, pDS = None, None


