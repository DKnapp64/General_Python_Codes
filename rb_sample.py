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

persdevfiles = ['persdev_mosaic_20190813.tif', 'persdev_mosaic_20190820.tif',
'persdev_mosaic_20190827.tif', 'persdev_mosaic_20190903.tif', 
'persdev_mosaic_20190910.tif', 'persdev_mosaic_20190917.tif', 
'persdev_mosaic_20190924.tif', 'persdev_mosaic_20191001.tif', 
'persdev_mosaic_20191008.tif', 'persdev_mosaic_20191015.tif', 
'persdev_mosaic_20191022.tif', 'persdev_mosaic_20191029.tif', 
'persdev_mosaic_20191105.tif', 'persdev_mosaic_20191112.tif', 
'persdev_mosaic_20191119.tif']

rbindexfiles = ['rbgood_index_20190813.tif', 'rbgood_index_20190820.tif',
               'rbgood_index_20190827.tif', 'rbgood_index_20190903.tif',
               'rbgood_index_20190910.tif', 'rbgood_index_20190917.tif',
               'rbgood_index_20190924.tif', 'rbgood_index_20191001.tif',
               'rbgood_index_20191008.tif', 'rbgood_index_20191015.tif',
               'rbgood_index_20191022.tif', 'rbgood_index_20191029.tif',
               'rbgood_index_20191105.tif', 'rbgood_index_20191112.tif',
               'rbgood_index_20191119.tif']

basefile = 'baseline_rb.tif'
baseDS = gdal.Open(basefile, gdal.GA_ReadOnly)
bgt = baseDS.GetGeoTransform()
## basedata = baseDS.GetRasterBand(1).ReadAsArray()
basedata = np.load('basedata.npy', mmap_mode='r')
baseDS = None

for j,rbname in enumerate(rbmosfiles):
  thedate = os.path.splitext(os.path.basename(persdevfiles[j]))[0][-8:]

  print('Started Working on %s' % (thedate))

##   rbDS = gdal.Open(rbname, gdal.GA_ReadOnly)
##   rgt = rbDS.GetGeoTransform()
##   rbdata = rbDS.GetRasterBand(1).ReadAsArray()
  indexDS = gdal.Open(rbindexfiles[j], gdal.GA_ReadOnly)
  igt = indexDS.GetGeoTransform()
##   pDS = gdal.Open(rbname, gdal.GA_ReadOnly)
##   pdata = pDS.GetRasterBand(1).ReadAsArray()

##   if not np.allclose(igt, rgt, atol=0.001):
##     print('This image %s does not match Geospatially..exiting' % (os.path.basename(rbname)))
##     baseDS, rbDS, indexDS = None, None, None
##     sys.exit(0)
     
##   if (indexDS.RasterXSize != rbDS.RasterXSize) or (indexDS.RasterYSize != rbDS.RasterYSize):
##     print('This image %s does not have same dimensions..exiting' % (os.path.basename(rbname)))
##     baseDS, rbDS, indexDS = None, None, None
##     sys.exit(0)

  gabove = indexDS.GetRasterBand(1).ReadAsArray().astype(np.bool)
  numabove = np.sum(gabove)
  indexabove = np.nonzero(gabove)
  randabove = np.random.randint(low=0, high=numabove, size=20000)
##   pabove = pdata[indexabove[0][randabove], indexabove[1][randabove]]
##   rabove = rbdata[indexabove[0][randabove], indexabove[1][randabove]]
##   baseabove = basedata[indexabove[0][randabove], indexabove[1][randabove]]
  np.save('index_row_above_'+thedate+'.npy', indexabove[0][randabove])  
  np.save('index_col_above_'+thedate+'.npy', indexabove[1][randabove])  

  del gabove
  del indexabove

  gbelow = indexDS.GetRasterBand(2).ReadAsArray().astype(np.bool)

  numbelow = np.sum(gbelow)
  indexbelow = np.nonzero(gbelow)
  del gbelow

  randbelow = np.random.randint(low=0, high=numbelow, size=20000)
##   pbelow = pdata[indexbelow[0][randbelow], indexbelow[1][randbelow]]
##   rbelow = rbdata[indexbelow[0][randbelow], indexbelow[1][randbelow]]
##   basebelow = basedata[indexbelow[0][randbelow], indexbelow[1][randbelow]]
  np.save('index_row_below_'+thedate+'.npy', indexbelow[0][randbelow])  
  np.save('index_col_below_'+thedate+'.npy', indexbelow[1][randbelow])  
  indexDS = None

  print('%s: Above: %d    Below: %d' % (rbname, numabove, numbelow))

##   outfile = 'bleach_data_extracted_'+thedate+'.npz'
## np.savez(outfile, pabove=pabove, pbelow=pbelow, rabove=rabove, rbelow=rbelow, 
##     baseabove=baseabove, basebelow=basebelow)
  ## rbDS, pDS = None, None
  print('Finished %s' % (thedate))


