#!/bin/env python3
import gdal, osr
import os, sys
import numpy as np
import glob
import subprocess

def main(infile):
  ## datestr = '20190731'
  ## layername = "sea_surface_temperature_anomaly"
  ## legendfile = "/scratch/dknapp4/Intensive/change_colorbar_legend.PNG" 

  ## legDS = gdal.Open(legendfile, gdal.GA_ReadOnly)
  ## legred = legDS.GetRasterBand(1).ReadAsArray() 
  ## leggreen = legDS.GetRasterBand(2).ReadAsArray() 
  ## legblue = legDS.GetRasterBand(3).ReadAsArray() 
  ## legy, legx = np.indices(legred.shape)
  ## print("Size of legend file: %d %d" % (legred.shape))
  ## legy, legx = np.indices(legred.shape)

  ## wildcard = "/scratch/nfabina/coral-reef-change-detection-hawaii/"+site+os.path.sep+datestr+os.path.sep+"threshold_"+datestr+"*.tif"
  ## example weekly filename L15-0137E-1136N_rb.tif_absolute.tif
  ## thisfile = glob.glob(wildcard)
  ## if (len(thisfile) == 1):
  ##   thisfile = thisfile[0]

  site = os.path.basename(infile)[0:15]
  datestr1 = os.path.dirname(infile).split('/')[-2]
  datestr2 = os.path.dirname(infile).split('/')[-1]
  ## datestr2 = os.path.splitext(os.path.basename(infile))[0][19:]
  indepth = "/scratch/dknapp4/Hawaii_Weekly/Unnormalized/"+datestr1+os.sep+site+"_depth.tif"
  print("Depth file: %s" % (indepth))
  depDS = gdal.Open(indepth, gdal.GA_ReadOnly)
  depthdata = depDS.GetRasterBand(1).ReadAsArray()
  depDS = None
  ## outtif = "/scratch/dknapp4/Intensive/change/"+site+os.path.sep+"threshold_"+site+"_"+datestr1+"_"+datestr2+"_rgb.tif"
  ## outkmz = "/scratch/dknapp4/Intensive/change/"+site+os.path.sep+"threshold_"+site+"_"+datestr1+"_"+datestr2+".kmz"
  outtif = "/scratch/dknapp4/Hawaii_Weekly/Differences/threshold_"+site+"_"+datestr1+"_"+datestr2+"_rgb.tif"
  outkmz = "/scratch/dknapp4/Hawaii_Weekly/Differences/threshold_"+site+"_"+datestr1+"_"+datestr2+".kmz"
  
  inDS = gdal.Open(infile, gdal.GA_ReadOnly)
  meta = inDS.GetMetadata()
  nodata = inDS.GetRasterBand(1).GetNoDataValue()
  gt = inDS.GetGeoTransform()
  threshdata = inDS.GetRasterBand(1).ReadAsArray()

  drv = gdal.GetDriverByName('GTiff')
  outDS = drv.Create(outtif, xsize=inDS.RasterXSize, ysize=inDS.RasterYSize, bands=3, eType=gdal.GDT_Byte)
  outDS.SetProjection(inDS.GetProjection())
  outDS.SetGeoTransform(gt)
  red = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.uint8)
  green = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.uint8)
  blue = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.uint8)
  inDS = None
  emptyvals = np.equal(threshdata, nodata)
  depthok = np.logical_and(np.less(depthdata, 1000), np.greater(depthdata, 0))
  low = np.logical_and(np.greater_equal(threshdata, 800), np.less(threshdata, 800+267))
  low2 = np.all(np.stack((low, depthok), axis=-1), axis=-1)
  medium = np.logical_and(np.greater_equal(threshdata, 800+267), np.less(threshdata, 800+2*267))
  medium2 = np.all(np.stack((medium, depthok), axis=-1), axis=-1)
  high = np.greater_equal(threshdata, 800+2*267)
  high2 = np.all(np.stack((high, depthok), axis=-1), axis=-1)
  low, medium, high = None, None, None
  red[low2] = 255 
  green[low2] = 255 
  blue[low2] = 1 
  red[medium2] = 1 
  green[medium2] = 255 
  blue[medium2] = 1 
  red[high2] = 255 
  green[high2] = 1 
  blue[high2] = 1 
  red[emptyvals] = 0
  green[emptyvals] = 0
  blue[emptyvals] = 0
  outDS.GetRasterBand(1).WriteArray(red)
  outDS.GetRasterBand(2).WriteArray(green)
  outDS.GetRasterBand(3).WriteArray(blue)
  outDS.GetRasterBand(1).SetNoDataValue(0)
  outDS.GetRasterBand(2).SetNoDataValue(0)
  outDS.GetRasterBand(3).SetNoDataValue(0)
  outDS.FlushCache()
  outDS = None
  cmd = ['/home/dknapp4/.conda/envs/davekenv/bin/gdal_translate','-of','KMLSUPEROVERLAY',outtif,outkmz,'-co','FORMAT=PNG']
  complete = subprocess.run(cmd, check=True)
  if (complete.returncode == 0):
    os.remove(outtif)

  
if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print("[ USAGE ] you must supply 1 argument: make_change_threshold_kmz.py infile")
    print("")
    sys.exit( 0 )

  main( sys.argv[1] )
