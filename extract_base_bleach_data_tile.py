#!/bin/env python3
import gdal
import numpy as np
import os, sys
import yaml
import glob
import datetime

tindex = int(sys.argv[1])

samptiles = ['baseline_ascending_L15-0116E-1151N.tif', 'baseline_ascending_L15-0116E-1153N.tif', 
'baseline_ascending_L15-0117E-1151N.tif', 'baseline_ascending_L15-0117E-1152N.tif', 
'baseline_ascending_L15-0117E-1153N.tif', 'baseline_ascending_L15-0136E-1135N.tif', 
'baseline_ascending_L15-0136E-1136N.tif', 'baseline_ascending_L15-0136E-1137N.tif', 
'baseline_ascending_L15-0136E-1138N.tif', 'baseline_ascending_L15-0136E-1139N.tif', 
'baseline_ascending_L15-0137E-1133N.tif', 'baseline_ascending_L15-0137E-1134N.tif', 
'baseline_ascending_L15-0137E-1135N.tif', 'baseline_ascending_L15-0137E-1136N.tif', 
'baseline_ascending_L15-0137E-1139N.tif', 'baseline_ascending_L15-0137E-1140N.tif', 
'baseline_ascending_L15-0137E-1141N.tif', 'baseline_ascending_L15-0138E-1133N.tif', 
'baseline_descending_L15-0112E-1150N.tif', 'baseline_descending_L15-0112E-1151N.tif', 
'baseline_descending_L15-0112E-1152N.tif', 'baseline_descending_L15-0113E-1151N.tif', 
'baseline_descending_L15-0113E-1152N.tif', 'baseline_descending_L15-0114E-1152N.tif', 
'baseline_descending_L15-0115E-1151N.tif', 'baseline_descending_L15-0115E-1152N.tif', 
'baseline_descending_L15-0115E-1153N.tif', 'baseline_descending_L15-0123E-1148N.tif', 
'baseline_descending_L15-0123E-1149N.tif', 'baseline_descending_L15-0124E-1147N.tif', 
'baseline_descending_L15-0124E-1148N.tif', 'baseline_descending_L15-0124E-1149N.tif', 
'baseline_descending_L15-0124E-1150N.tif', 'baseline_descending_L15-0125E-1147N.tif', 
'baseline_descending_L15-0125E-1148N.tif', 'baseline_descending_L15-0125E-1149N.tif', 
'baseline_descending_L15-0125E-1150N.tif', 'baseline_descending_L15-0126E-1147N.tif', 
'baseline_descending_L15-0126E-1148N.tif', 'baseline_descending_L15-0126E-1149N.tif', 
'baseline_descending_L15-0127E-1147N.tif', 'baseline_descending_L15-0127E-1148N.tif', 
'baseline_descending_L15-0128E-1146N.tif', 'baseline_descending_L15-0129E-1146N.tif', 
'baseline_descending_L15-0129E-1147N.tif', 'baseline_descending_L15-0130E-1144N.tif', 
'baseline_descending_L15-0130E-1145N.tif', 'baseline_descending_L15-0130E-1146N.tif', 
'baseline_descending_L15-0130E-1147N.tif', 'baseline_descending_L15-0131E-1144N.tif', 
'baseline_descending_L15-0131E-1145N.tif', 'baseline_descending_L15-0131E-1146N.tif', 
'baseline_descending_L15-0131E-1147N.tif', 'baseline_descending_L15-0132E-1143N.tif', 
'baseline_descending_L15-0132E-1144N.tif', 'baseline_descending_L15-0132E-1145N.tif', 
'baseline_descending_L15-0132E-1146N.tif', 'baseline_descending_L15-0132E-1147N.tif', 
'baseline_descending_L15-0133E-1143N.tif', 'baseline_descending_L15-0133E-1144N.tif', 
'baseline_descending_L15-0133E-1145N.tif', 'baseline_descending_L15-0133E-1146N.tif', 
'baseline_descending_L15-0134E-1143N.tif', 'baseline_descending_L15-0134E-1144N.tif', 
'baseline_descending_L15-0134E-1145N.tif', 'baseline_descending_L15-0135E-1143N.tif', 
'baseline_descending_L15-0135E-1144N.tif', 'baseline_descending_L15-0135E-1145N.tif', 
'baseline_descending_L15-0136E-1134N.tif', 'baseline_descending_L15-0136E-1144N.tif', 
'baseline_descending_L15-0136E-1145N.tif', 'baseline_descending_L15-0138E-1134N.tif', 
'baseline_descending_L15-0138E-1140N.tif', 'baseline_descending_L15-0138E-1141N.tif', 
'baseline_descending_L15-0139E-1134N.tif', 'baseline_descending_L15-0139E-1135N.tif', 
'baseline_descending_L15-0139E-1140N.tif', 'baseline_descending_L15-0140E-1135N.tif', 
'baseline_descending_L15-0140E-1140N.tif', 'baseline_descending_L15-0141E-1135N.tif', 
'baseline_descending_L15-0141E-1136N.tif', 'baseline_descending_L15-0141E-1138N.tif', 
'baseline_descending_L15-0141E-1139N.tif', 'baseline_descending_L15-0141E-1140N.tif', 
'baseline_descending_L15-0142E-1136N.tif', 'baseline_descending_L15-0142E-1137N.tif', 
'baseline_descending_L15-0142E-1138N.tif', 'baseline_descending_L15-0143E-1136N.tif', 
'baseline_descending_L15-0143E-1137N.tif']

thetile = samptiles[tindex]
tid = os.path.splitext(samptiles[tindex])[0][-15:]

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
coralfile = 'CoralNew/coral_mask_mosaic.tif'

coralDS = gdal.Open(coralfile, gdal.GA_ReadOnly)
baseDS = gdal.Open(basefile, gdal.GA_ReadOnly)
cgt = coralDS.GetGeoTransform()
bgt = baseDS.GetGeoTransform()

sampDS = gdal.Open(thetile, gdal.GA_ReadOnly)
sampgt = sampDS.GetGeoTransform()
proj = sampDS.GetProjection()
xoffset = round((sampgt[0]-cgt[0])/sampgt[1])
yoffset = round((sampgt[3]-cgt[3])/sampgt[5])
xsize = sampDS.RasterXSize
ysize = sampDS.RasterYSize
sampDS = None

if not np.allclose(cgt, bgt, atol=0.001):
  print('Coral and Baseline images do not match Geospatially..exiting')
  coralDS, baseDS = None, None
  sys.exit(0)

if (coralDS.RasterXSize != baseDS.RasterXSize) or (coralDS.RasterYSize != baseDS.RasterYSize):
  print('Coral and Baseline images do not have the same dimensions..exiting')
  coralDS, baseDS = None, None
  sys.exit(0)
  
coralmask = coralDS.GetRasterBand(1).ReadAsArray(xoffset, yoffset, xsize, ysize)
basedata = baseDS.GetRasterBand(1).ReadAsArray(xoffset, yoffset, xsize, ysize)
coralmaskon = np.equal(coralmask, 1)
basedataon = np.logical_and(np.not_equal(basedata, -9999), np.not_equal(basedata, 0))

drv = gdal.GetDriverByName('GTiff')

for j,rbname in enumerate(rbmosfiles):
  thedate = os.path.splitext(os.path.basename(persdevfiles[j]))[0][-8:]

  print('Started Working on %s %s' % (thedate, tid))

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

  rbdata = rbDS.GetRasterBand(1).ReadAsArray(xoffset, yoffset, xsize, ysize)
  rbon = np.logical_and(np.not_equal(rbdata, -9999), np.not_equal(rbdata, 0))
  
  pDS = gdal.Open(persdevfiles[j], gdal.GA_ReadOnly)
  pdata = pDS.GetRasterBand(1).ReadAsArray(xoffset, yoffset, xsize, ysize)
  above = np.greater_equal(pdata, 2)
  below = np.less(pdata, 2)
  allgood = np.all(np.dstack((coralmaskon, basedataon, rbon)), axis=-1)

  print('Stacked Coralmask, Baseline, and Rb')
  gabove = np.logical_and(above, allgood)
  gbelow = np.logical_and(below, allgood)
  numabove = np.sum(gabove)
  numbelow = np.sum(gbelow)
  print('%s: Above: %d    Below: %d' % (rbname, numabove, numbelow))
  outfile = 'rb_baseline_bleach_data_'+thedate+'_'+tid+'.tif'
  outDS = drv.Create(outfile, xsize, ysize, 2, gdal.GDT_Byte)
  outDS.SetGeoTransform(sampgt)
  outDS.SetProjection(proj)
  outDS.GetRasterBand(1).WriteArray(gabove.astype(np.uint8))
  outDS.GetRasterBand(2).WriteArray(gbelow.astype(np.uint8))
  ## np.savez(outfile, pabove=pabove, pbelow=pbelow, rabove=rabove, rbelow=rbelow, 
  ##   baseabove=baseabove, basebelow=basebelow)
  outDS, rbDS, pDS = None, None, None

coralDS, baseDS = None, None
print('Finished %s %s' % (thedate, tid))
