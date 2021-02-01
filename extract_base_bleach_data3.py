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

rballfile = 'rb_on_thru_time.tif'
persdevfile = 'persdev_mosaic_20191119.tif'

basefile = 'baseline_rb.tif'
coralfile = 'CoralNew/coral_mask_mosaic.tif'

coralDS = gdal.Open(coralfile, gdal.GA_ReadOnly)
baseDS = gdal.Open(basefile, gdal.GA_ReadOnly)

if not os.path.exists('rbon.npy'):
  rballDS = gdal.Open(rballfile, gdal.GA_ReadOnly)
  rbon = rballDS.GetRasterBand(1).ReadAsArray().astype(np.bool)
  rballDS = None
  np.save('rbon.npy', rbon)
else:
  rbon = np.load('rbon.npy', mmap_mode='r')

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
 
if not os.path.exists('coralmaskon.npy'):
  coralmask = coralDS.GetRasterBand(1).ReadAsArray()
  coralmaskon = np.equal(coralmask, 1)
  np.save('coralmaskon.npy', coralmaskon)
else:
  coralmaskon = np.load('coralmaskon.npy', mmap_mode='r')

if not os.path.exists('basedata.npy') or not os.path.exists('basedataon.npy'):
  basedata = baseDS.GetRasterBand(1).ReadAsArray()
  basedataon = np.logical_and(np.not_equal(basedata, -9999), np.not_equal(basedata, 0))
  np.save('basedataon.npy', basedataon)
  np.save('basedata.npy', basedata)
else:
  basedataon = np.load('basedataon.npy', mmap_mode='r')
  basedata = np.load('basedata.npy', mmap_mode='r')
  
coralmask = None

pDS = gdal.Open(persdevfile, gdal.GA_ReadOnly)
pdata = pDS.GetRasterBand(1).ReadAsArray()
for uval in range(2,16):
  index = np.equals(pdata, uval)
  np.save('pdata%02d.npy' % (uval), pdata)

pdata = np.load('pdata.npy', mmap_mode='r')                                       

for j,rbname in enumerate(rbmosfiles):
  tempdate = os.path.splitext(os.path.basename(rbname))[0][-8:]
  thedate = (datetime.date(int(tempdate[0:4]), int(tempdate[4:6]), int(tempdate[6:8])) + datetime.timedelta(days=1)).strftime('%Y%m%d')

  print('Started Working on %s' % (thedate))

  rbDS = gdal.Open(rbname, gdal.GA_ReadOnly)
  rgt = rbDS.GetGeoTransform()

  if not os.path.exists('rbdata_'+thedate+'.npy'):
    rbdata = rbDS.GetRasterBand(1).ReadAsArray()
    rbon = np.logical_and(np.not_equal(rbdata, -9999), np.not_equal(rbdata, 0))
    np.save('rbon_'+thedate+'.npy', rbon)
  
  if not os.path.exists('above_'+thedate+'.npy'):
    above = np.greater_equal(pdata, 2)
    np.save('above_'+thedate+'.npy', above)
  else:
    above = np.load('above_'+thedate+'.npy', mmap_mode='r')                                       

  if not os.path.exists('below_'+thedate+'.npy'):
    below = np.greater_equal(pdata, 2)
    np.save('below_'+thedate+'.npy', below)
  else:
    below = np.load('below_'+thedate+'.npy', mmap_mode='r')                                       
    
  if not os.path.exists('allgood_'+thedate+'.npy'):
    allgood = np.all(np.dstack((coralmaskon, basedataon, rbon)), axis=-1)
    np.save('allgood_'+thedate+'.npy', allgood)                                   
  else:
    allgood = np.load('allgood_'+thedate+'.npy', mmap_mode='r')                                       

  print('Stacked Coralmask, Baseline, and Rb')

  if not os.path.exists('gabove_'+thedate+'.npy'):
    gabove = np.logical_and(above, allgood)
  else:
    gabove = np.load('gabove_'+thedate+'.npy', mmap_mode='r')                                       

  if not os.path.exists('gbelow_'+thedate+'.npy'):
    gbelow = np.logical_and(below, allgood)
  else:
    gbelow = np.load('gbelow_'+thedate+'.npy', mmap_mode='r')                                       

  numabove = np.sum(gabove)
  numbelow = np.sum(gbelow)

  print('%s: Above: %d    Below: %d' % (rbname, numabove, numbelow))
  
  if not os.path.exists('indexbelow_'+thedate+'.npy'):
    indexbelow = np.nonzero(gbelow)
  else:
    indexbelow = np.load('indexbelow_'+thedate+'.npy', mmap_mode='r')                                       

  if not os.path.exists('indexabove_'+thedate+'.npy'):
    indexabove = np.nonzero(gabove)
  else:
    indexabove = np.load('indexabove_'+thedate+'.npy', mmap_mode='r')                                       

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
  print('Finished %s' % (thedate))


