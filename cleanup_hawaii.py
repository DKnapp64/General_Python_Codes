#!/bin/env python3
import gdal, ogr, osr
import numpy as np
import os, sys
import warnings

def main(tileid):

  prefix = 'Persistent_Deviation/persdev_20191014_to_20191021'

  infile1 = prefix + os.path.sep + 'persistant_deviation_descending_' + tileid + '_20191022.tif'
  infile2 = prefix + os.path.sep + 'persistant_deviation_ascending_' + tileid + '_20191022.tif'
  depthfile = 'depth_ll' + os.path.sep + tileid + '_depth.tif'
  outfile = prefix + os.path.sep + tileid + '_20191014_to_20191021_cleancombo.tif'

  if os.path.exists(infile1):
    inDS1 = gdal.Open(infile1, gdal.GA_ReadOnly)
  if os.path.exists(infile2):
    inDS2 = gdal.Open(infile2, gdal.GA_ReadOnly)
  
  if not (os.path.exists(infile1) or os.path.exists(infile2)):
    print("Neither Ascending nor Descending files exist.  exiting")
    sys.exit(0)

  ## get data type
  datatype = inDS1.GetRasterBand(1).DataType
  
  # Create for target raster the same projection as for the value raster
  raster_srs = osr.SpatialReference()
  proj = inDS1.GetProjection()
  
  outXsize = inDS1.RasterXSize
  outYsize = inDS1.RasterYSize
  
  ## get geotransform of mosaic bounds
  gt = inDS1.GetGeoTransform()
  
  if (inDS1 is not None):
    indata1 = inDS1.GetRasterBand(1).ReadAsArray()
    bad1 = np.logical_or(np.equal(indata1, -9999), np.equal(indata1, np.nan))
    ## indata1[bad1] = np.nan
    indata1[bad1] = 0
  if (inDS2 is not None):
    indata2 = inDS2.GetRasterBand(1).ReadAsArray()
    bad2 = np.logical_or(np.equal(indata2, -9999), np.equal(indata2, np.nan))
    ## indata2[bad2] = np.nan
    indata2[bad2] = 0
  
  if (indata1 is not None and indata2 is not None):
    stack = np.stack((indata1, indata2), axis=-1)
    ## meanvals = np.nanmean(stack, axis=-1)
    sumvals = np.sum(stack, axis=-1)
  else:
    if (indata1 is not None and indata2 is None):
      sumvals = indata1
    if (indata2 is not None and indata1 is None):
      sumvals = indata2

  mDS = gdal.Open(depthfile, gdal.GA_ReadOnly)
  mask = mDS.GetRasterBand(1).ReadAsArray()

  with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    masktf = np.logical_or(np.less(mask, 0.0), np.greater_equal(mask, 10.0)) 

  zerovals = np.equal(sumvals,0)
  sumvals[zerovals] = -9999.0
  sigvals = np.less(sumvals, 2)
  sumvals[sigvals] = -9999.0

  sumvals[masktf] = -9999.0
  thenans = np.isnan(sumvals)
  sumvals[thenans] = -9999.0

  driver = gdal.GetDriverByName('GTiff')
  outDS = driver.Create(outfile, outXsize, outYsize, 1, datatype, options=['TILED=YES', 'COMPRESS=LZW']) 
  outDS.SetGeoTransform(gt)
  outDS.SetProjection(proj)
  outDS.GetRasterBand(1).SetNoDataValue(-9999.0)
  ## outDS.GetRasterBand(1).WriteArray(meanvals)
  outDS.GetRasterBand(1).WriteArray(sumvals)
  outDS.FlushCache()

  inDS1, inDS2, mDS, outDS = None, None, None, None

if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print("[ USAGE ] you must supply 1 argument: cleanup_hawaii.py tileid")
    sys.exit( 0 )

  main( sys.argv[1] )
