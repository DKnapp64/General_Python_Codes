#!/bin/env python3
import gdal
import ogr, osr
import numpy as np
import os, sys
import math

def main(inimg, inmask, inshp, outtxt):

## OGRFeature(points_trees_brown_green_utm5n):0
##   region (String) = Hilo
##   2019 (String) = b
##   2018 (String) = g
##   2017 (String) = g
##   2016 (String) = g
##   Crown ID (String) = 1
##   wa_mean (Real) = -1.057632768696005
##   nic_mean (Real) = -27.397725373506546
##   Phe_mean (Real) = -129.686729431152344
##   N_mean (Real) = 0.272374899549918
##   LMA_mean (Real) = 382.030143044211627
##   Lig_mean (Real) = 17.578550728884611
##   Chl_mean (Real) = 0.762941441752694

  if os.path.exists(inimg):
    inDS = gdal.Open(inimg, gdal.GA_ReadOnly)
  else:
    print('File %s doe not exist...quitting' % (inimg))
    sys.exit(0)

  igt = inDS.GetGeoTransform()
  iulx = igt[0]
  iuly = igt[3]
  ixres = igt[1]
  iyres = igt[5]

  if os.path.exists(inmask):
    maskDS = gdal.Open(inmask, gdal.GA_ReadOnly)
  else:
    print('File %s doe not exist...quitting' % (inmask))
    inDS = None
    sys.exit(0)

  mgt = maskDS.GetGeoTransform()
  mulx = mgt[0]
  muly = mgt[3]
  mxres = mgt[1]
  myres = mgt[5]

  barraylist = []
  for b in range(inDS.RasterCount):
    theband = inDS.GetRasterBand(b+1)
    bandit = theband.ReadAsArray()
    barraylist.append(bandit)
 
  maskBand = mDS.GetRasterBand(1).ReadAsArray()

  shpDS = ogr.GetDriverByName("ESRI Shapefile").Open(inshp)  
  layer = shpDS.GetLayer()
  geomtype = layer.GetGeomType()
  if (geomtype != 1):
    print('File %s doe not exist...quitting' % (inimg))
    sys.exit(0)
    
  featCnt = layer.GetFeatureCount() 

  f = open(outtxt, 'w')

  for thisFeat in range(featCnt):
    feat = layer.GetNextFeature()  
    thename = feat.GetField("Crown ID")
    geom = feat.GetGeometryRef() 
    utmpnt = geom.GetPoint()
    ipix = int(math.floor((utmpnt[0] - iulx)/igt[1]))
    ilin = int(math.floor((utmpnt[1] - iuly)/igt[5]))
    if ((0 < ipix < inDS.RasterXSize) and (0 < ilin < inDS.RasterYSize)):
      bigstring = ("%s, %s, ") % (thename, inimg)
      for b in range(inDS.RasterCount-1):
        bigstring += "%8.4f, " % (barraylist[b][ilin,ipix]) 
      bigstring += "%8.4f" % (barraylist[-1][ilin,ipix]) 
      f.write(bigstring)
    mpix = int(math.floor((utmpnt[0] - mulx)/mgt[1]))
    mlin = int(math.floor((utmpnt[1] - muly)/mgt[5]))
    if ((0 < mpix < mDS.RasterXSize) and (0 < mlin < mDS.RasterYSize)):
      bigstring += ", %4d\n" % (maskBand[ilin,ipix]) 
      f.write(bigstring)

  for band in barraylist:
    band = None  
  maskBand = None

  shpDS, layer = None, None 
  inDS, mDS = None, None
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
