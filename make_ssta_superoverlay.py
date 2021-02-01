#!/bin/env python3
import gdal, osr
import os, sys
import numpy as np
import glob
import math
from datetime import datetime, timedelta
from matplotlib import cm
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import subprocess

def main(datestr):
  ## datestr = '20190731'
  layername = "sea_surface_temperature_anomaly"
  legendfile = "/scratch/dknapp4/ssta/ssta_colorbar_legend_50p.PNG" 

  legDS = gdal.Open(legendfile, gdal.GA_ReadOnly)
  legred = legDS.GetRasterBand(1).ReadAsArray() 
  leggreen = legDS.GetRasterBand(2).ReadAsArray() 
  legblue = legDS.GetRasterBand(3).ReadAsArray() 
  legy, legx = np.indices(legred.shape)
  print("Size of legend file: %d %d" % (legred.shape))
  legy, legx = np.indices(legred.shape)
  ## NETCDF:"2015/ct5km_ssta_v3.1_20150101.nc":sea_surface_temperature_anomaly
  ## 2019/ct5km_ssta_v3.1_20190803.nc
  thisfile = "/scratch/dknapp4/ssta/"+datestr[0:4]+os.path.sep+"ct5km_ssta_v3.1_"+datestr+".nc"
  outtif = os.path.dirname(thisfile)+os.path.sep+"sstanomaly_"+datestr+".tif"
  outkmz = "sstanomaly_"+datestr+".kmz"
  
  inDS = gdal.Open("NETCDF:{0}:{1}".format(thisfile, layername), gdal.GA_ReadOnly)
  meta = inDS.GetMetadata()
  scale = float(meta['sea_surface_temperature_anomaly#scale_factor'])
  nodata = int(meta['sea_surface_temperature_anomaly#_FillValue'])
  gt = (-180.0, 0.05, 0.0, 90.0, 0.0, -0.05)
  ulx = 381
  uly = 1337
  lrx = 521
  lry = 1442
  xdim = lrx-ulx+1 
  ydim = lry-uly+1
  legy = legy + (ydim*8 - legy.max()) - 1
  sstadata = inDS.GetRasterBand(1).ReadAsArray(ulx,uly,xdim,ydim)
  ## expand data in both dimensions by 2
  sstadata2 = np.repeat(np.repeat(sstadata, 8).reshape(sstadata.shape[0], sstadata.shape[1]*8), 8, axis=0)
  print("Size of resized SSDT Anomaly data: %d %d" % (sstadata2.shape))
  inDS = None
  newgt = (-180.0+ulx*0.05, 0.05/8, 0.0, 90.0-uly*0.05, 0.0, -0.05/8)
  drv = gdal.GetDriverByName('GTiff')
  outDS = drv.Create(outtif, xsize=xdim*8, ysize=ydim*8, bands=3, eType=gdal.GDT_Byte)
  mysrs = osr.SpatialReference()
  mysrs.ImportFromEPSG(4326)
  outDS.SetProjection(mysrs.ExportToWkt())
  outDS.SetGeoTransform(newgt)
  red = np.zeros((ydim, xdim), dtype=np.uint8)
  green = np.zeros((ydim, xdim), dtype=np.uint8)
  blue = np.zeros((ydim, xdim), dtype=np.uint8)
  emptyvals = np.equal(sstadata2, nodata)
  minval = -255
  maxval = 255
  print(("Min Max: %d  %d") % (minval, maxval))
  new_arr = ((sstadata2 - minval) * (1/(maxval - minval) * 254)+1).astype('uint8')
  ## colors = bokeh.palettes.inferno(256)
  thereds = np.zeros(256, dtype=np.uint8)
  thegreens = np.zeros(256, dtype=np.uint8)
  theblues = np.zeros(256, dtype=np.uint8)
  for k in range(256):
    thereds[k] = round(cm.jet(k)[0] * 255)
    thegreens[k] = round(cm.jet(k)[1] * 255)
    theblues[k] = round(cm.jet(k)[2] * 255)
  index = np.equal(thereds, 0)
  thereds[index] = 1
  index = np.equal(thegreens, 0)
  thegreens[index] = 1
  index = np.equal(theblues, 0)
  theblues[index] = 1
  red = thereds[new_arr]
  green = thegreens[new_arr]
  blue = theblues[new_arr]
  red[emptyvals] = 0
  green[emptyvals] = 0
  blue[emptyvals] = 0
  index = np.equal(legred, 0)
  leggreen[index] = 1
  index = np.equal(leggreen, 0)
  leggreen[index] = 1
  index = np.equal(legblue, 0)
  legblue[index] = 1
  red[legy, legx] = legred
  green[legy, legx] = leggreen
  blue[legy, legx] = legblue
  outDS.GetRasterBand(1).WriteArray(red)
  outDS.GetRasterBand(2).WriteArray(green)
  outDS.GetRasterBand(3).WriteArray(blue)
  outDS.GetRasterBand(1).SetNoDataValue(0)
  outDS.GetRasterBand(2).SetNoDataValue(0)
  outDS.GetRasterBand(3).SetNoDataValue(0)
  outDS.FlushCache()
  outDS = None
  img = Image.open(outtif)
  draw = ImageDraw.Draw(img)
  font = ImageFont.truetype("/usr/share/fonts/msttcorefonts/arial.ttf", size=40) 
  ## font = ImageFont.truetype("/usr/share/fonts/gnu-free/FreeSans.ttf", size=75) 
  draw.text((25,595), datestr, (1,1,1), font=font)
  img.save(os.path.splitext(outtif)[0]+'2.tif')
  img = None
  tmp1DS = gdal.Open(outtif, gdal.GA_Update)
  tmp2DS = gdal.Open(os.path.splitext(outtif)[0]+'2.tif', gdal.GA_ReadOnly)
  tmp1DS.GetRasterBand(1).WriteArray(tmp2DS.GetRasterBand(1).ReadAsArray())
  tmp1DS.GetRasterBand(2).WriteArray(tmp2DS.GetRasterBand(2).ReadAsArray())
  tmp1DS.GetRasterBand(3).WriteArray(tmp2DS.GetRasterBand(3).ReadAsArray())
  tmp1DS, tmp2DS = None, None
  cmd = ['/home/dknapp4/.conda/envs/davekenv/bin/gdal_translate','-of','KMLSUPEROVERLAY',outtif,outkmz,'-co','FORMAT=PNG']
  complete = subprocess.run(cmd, check=True)
  if (complete.returncode == 0):
    os.remove(outtif)
    os.remove(os.path.splitext(outtif)[0]+'2.tif')

  
if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print("[ USAGE ] you must supply 1 argument: make_ssta_superoverlay.py datestr")
    print("")
    sys.exit( 0 )

  main( sys.argv[1] )
