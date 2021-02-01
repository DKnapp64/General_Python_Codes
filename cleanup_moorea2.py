#!/bin/env python3
import gdal, ogr, osr
import numpy as np
import os, sys
import warnings

def main(infile):

  tileid = os.path.basename(infile).split('_')[3]
  datepart = os.path.splitext(os.path.basename(infile))[0].split('_')[-1]
  ## dirparts = infile.split('/')
  depthfile = '/data/gdcsdata/Research/Researcher/Knapp/Moorea_Weekly/depth' + os.path.sep + tileid + '_depth.tif'
  ## outfile = '/data/gdcsdata/Research/Researcher/Knapp/Moorea_Weekly/AscendingDescending/Persistent_Deviation/' + os.path.splitext(infile)[0] + '_cleaned.tif'
  ## outfile = '/data/gdcsdata/Research/Researcher/Knapp/Moorea_Weekly/AscendingDescending/Persistent_Deviation/' + dirparts[-2] + '/' + os.path.splitext(os.path.basename(infile))[0] + '_cleaned.tif'
  outfile = '/data/gdcsdata/Research/Researcher/Knapp/Moorea_Weekly/AscendingDescending/Persistent_Deviation/' + datepart + '/' + os.path.splitext(os.path.basename(infile))[0] + '_cleaned.tif'
  print("tileID: %s" % (tileid))
  infile = '/data/gdcsdata/Research/Researcher/Knapp/Moorea_Weekly/AscendingDescending/Persistent_Deviation/' + datepart + '/' + infile

  if os.path.exists(infile):
    inDS = gdal.Open(infile, gdal.GA_ReadOnly)
  else:
    print("File %s does not exist" % (infile))
    sys.exit(0)

  ## get data type
  datatype = inDS.GetRasterBand(1).DataType
  
  # Create for target raster the same projection as for the value raster
  raster_srs = osr.SpatialReference()
  proj = inDS.GetProjection()
  
  outXsize = inDS.RasterXSize
  outYsize = inDS.RasterYSize
  
  ## get geotransform of mosaic bounds
  gt = inDS.GetGeoTransform()
  
  if (inDS is not None):
    indata1 = inDS.GetRasterBand(1).ReadAsArray()
    indata2 = inDS.GetRasterBand(2).ReadAsArray()
    bad = np.logical_or(np.equal(indata1, -9999), np.equal(indata1, np.nan))
    indata1[bad] = 0
    indata2[bad] = 0
  else:
    print("File %s could not be opened" % (infile))
    sys.exit(0)
  
  mDS = gdal.Open(depthfile, gdal.GA_ReadOnly)
  mask = mDS.GetRasterBand(1).ReadAsArray()

  with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    masktf = np.logical_or(np.less(mask, 0.0), np.greater(mask,10.0))

  sigvals = np.less(indata1, 2)
  thenans = np.isnan(indata1)

  indata1[sigvals] = 0
  indata1[masktf] = 0
  indata1[thenans] = 0
  indata2[sigvals] = 0
  indata2[masktf] = 0
  indata2[thenans] = 0

  driver = gdal.GetDriverByName('GTiff')
  outDS = driver.Create(outfile, outXsize, outYsize, 2, datatype, options=['COMPRESS=LZW', 'TILED=YES']) 
  outDS.SetGeoTransform(gt)
  outDS.SetProjection(proj)
  outDS.GetRasterBand(1).SetNoDataValue(0)
  outDS.GetRasterBand(1).WriteArray(indata1)
  outDS.GetRasterBand(2).SetNoDataValue(0)
  outDS.GetRasterBand(2).WriteArray(indata2)
  outDS.FlushCache()

  inDS, mDS, outDS = None, None, None

if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print("[ USAGE ] you must supply 1 argument: cleanup_moorea2.py infile")
    sys.exit( 0 )

  main( sys.argv[1] )
