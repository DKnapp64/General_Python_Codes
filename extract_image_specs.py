#!/bin/env python3
import gdal
import ogr, osr
import numpy as np
import os, sys
import math

def main(inimg, inshp, outtxt):

  inDS = gdal.Open(inimg, gdal.GA_ReadOnly)
  gt = inDS.GetGeoTransform()
  ulx = gt[0]
  uly = gt[3]
  xres = gt[1]
  yres = gt[5]

  barraylist = []
  for b in range(inDS.RasterCount):
    theband = inDS.GetRasterBand(b+1)
    bandit = theband.ReadAsArray()
    barraylist.append(bandit)
 
  shpDS = ogr.GetDriverByName("ESRI Shapefile").Open(inshp)  
  layer = shpDS.GetLayer()
  featCnt = layer.GetFeatureCount() 

  f = open(outtxt, 'w')

  for thisFeat in range(featCnt):
    feat = layer.GetNextFeature()  
    thename = (feat.GetField("specname"))[0:9]
    geom = feat.GetGeometryRef() 
    utmpnt = geom.GetPoint()
    pix = int(math.floor((utmpnt[0] - ulx)/gt[1]))
    lin = int(math.floor((utmpnt[1] - uly)/gt[5]))
    if ((0 < pix < inDS.RasterXSize) and (0 < lin < inDS.RasterYSize)):
      bigstring = ("%s, %s, ") % (thename, inimg)
      for b in range(inDS.RasterCount-1):
        bigstring += "%8.4f," % (barraylist[b][lin,pix]/10000.0) 
      bigstring += "%8.4f\n" % (barraylist[-1][lin,pix]/10000.0) 
      f.write(bigstring)

  for band in barraylist:
    band = None  

  shpDS, layer = None, None 
  inDS = None
  f.close()

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ ERROR ] you must supply 3 arguments: extract_image_specs.py inimg inshp outtxt")
    print("where:")
    print("    inimg = input image.")
    print("    inshp = input point shapefile.")
    print("    outtxt = output text file with extracted spectral values from image for each point in the shapefile.")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3] )
