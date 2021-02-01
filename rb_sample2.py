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

basefile = 'baseline_rb.tif'
baseDS = gdal.Open(basefile, gdal.GA_ReadOnly)
bgt = baseDS.GetGeoTransform()
## basedata = baseDS.GetRasterBand(1).ReadAsArray()
basedata = np.load('basedata.npy', mmap_mode='r')
baseDS = None

for j,rbname in enumerate(rbmosfiles):
  thedate = os.path.splitext(os.path.basename(persdevfiles[j]))[0][-8:]
  print('Started Working on %s' % (thedate))

  arows =  np.load('index_row_above_'+thedate+'.npy')
  acols =  np.load('index_col_above_'+thedate+'.npy')
  brows =  np.load('index_row_below_'+thedate+'.npy')
  bcols =  np.load('index_col_below_'+thedate+'.npy')

  rbDS = gdal.Open(rbname, gdal.GA_ReadOnly)
  rbdata = rbDS.GetRasterBand(1).ReadAsArray()

  rabove = rbdata[arows, acols]
  rbelow = rbdata[brows, bcols]
  del rbdata
  rbdata = None

  pDS = gdal.Open(rbname, gdal.GA_ReadOnly)
  pdata = pDS.GetRasterBand(1).ReadAsArray()

  pabove = pdata[arows, acols]
  pbelow = pdata[brows, bcols]
  del pdata
  pDS = None

  baseabove = basedata[arows, acols]
  basebelow = basedata[brows, bcols]
 
  outfile = 'bleach_data_extracted_'+thedate+'.npz'
  np.savez(outfile, pabove=pabove, pbelow=pbelow, rabove=rabove, rbelow=rbelow, 
    baseabove=baseabove, basebelow=basebelow)
  print('Finished %s' % (thedate))


