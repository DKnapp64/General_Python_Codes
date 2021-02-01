#!/bin/env python3
import gdal
import numpy as np
import osr
import os, sys

def main(infile1, infile2, maskname1, maskname2, difffile):

  ## maskname1 = infile1[0:-18]+'_mosaic_mask.tif'
  ## maskname2 = infile2[0:-18]+'_mosaic_mask.tif'

  try:
    in1DS = gdal.Open(infile1, gdal.GA_ReadOnly)
  except:
    print("Error: Could not open file %s to read." % (infile1))
    sys.exit(1)

  try:
    in2DS = gdal.Open(infile2, gdal.GA_ReadOnly)
  except:
    print("Error: Could not open file %s to read." % (infile1))
    in1DS = None
    sys.exit(1)

  try:
    mask1DS = gdal.Open(maskname1, gdal.GA_ReadOnly)
  except:
    print("Error: Could not open file %s to read." % (maskname1))
    sys.exit(1)

  try:
    mask2DS = gdal.Open(maskname2, gdal.GA_ReadOnly)
  except:
    print("Error: Could not open file %s to read." % (maskname2))
    in1DS = None
    sys.exit(1)

  blue1 = in1DS.GetRasterBand(1).ReadAsArray()
  blue2 = in2DS.GetRasterBand(1).ReadAsArray()
  
  if ((blue1.shape[0] == blue2.shape[0]) and (blue1.shape[1] == blue2.shape[1])):
    missing = np.logical_or(np.equal(blue1, -9999), np.equal(blue2, -9999))
    ## differ = np.logical_greater((blue2-blue1), 600)
    ## differ[missing] = False
    differ = blue2 - blue1
    lowdiff = np.less(differ, 600)
    differ[lowdiff] = 0
    differ[missing] = 0
  else:
    print("Error: Array dimensions do not match.")
    in1DS, in2DS = None, None
    sys.exit(1)
  
  mask1a = mask1DS.GetRasterBand(1).ReadAsArray()
  mask1b = mask1DS.GetRasterBand(7).ReadAsArray()
  mask2a = mask2DS.GetRasterBand(1).ReadAsArray()
  mask2b = mask2DS.GetRasterBand(7).ReadAsArray()
  clear1 = mask1a.astype(bool)
  conf1 = np.greater(mask1b, 70)
  clear2 = mask2a.astype(bool)
  conf2 = np.greater(mask2b, 70)
  good1 = np.logical_and(clear1, conf1)
  good2 = np.logical_and(clear2, conf2)
  suspect = np.logical_not(np.logical_and(good1, good2))
  differ[suspect] = 0

  drv = gdal.GetDriverByName('GTiff')
  outDS = drv.Create(difffile, in1DS.RasterXSize, in1DS.RasterYSize, 1, gdal.GDT_Int16, ['COMPRESS=LZW'])
  gt = in1DS.GetGeoTransform()
  ## proj = osr.SpatialReference()
  ## proj.ImportfromWkt(in1DS.GetProjection())
  outDS.SetGeoTransform(gt)
  outDS.SetProjection(in1DS.GetProjection())
  outDS.GetRasterBand(1).WriteArray(differ)
  outDS.FlushCache()
  in1DS, in2DS, outDS = None, None, None
  mask1DS, mask2DS = None, None
  
if __name__ == "__main__":

  if len( sys.argv ) != 6:
    print("[ ERROR ] you must supply 5 arguments: make_differ.py beforefile afterfile beforemask aftermask differfile")
    print("    beforefile = the Rb image of Before state.")
    print("    afterfile = the Rb image of After state.")
    print("    beforemask = the mask image of Before state.")
    print("    aftermask = the mask image of After state.")
    print("    differfile = the output difference image.  Pixels with difference greater than 400.")
    print("")

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

