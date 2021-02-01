#!/bin/env python3
import gdal, ogr, osr
import math
import numpy as np
import os, sys
import re, fnmatch
import csv

def main(inimgtemplate, inbgrcsv, inshape, outimg):

  inDS = gdal.Open(inimgtemplate, gdal.GA_ReadOnly)
  gt = inDS.GetGeoTransform()
  ns = inDS.RasterXSize
  nl = inDS.RasterYSize
  print(gt)
  
  specrows = []
  with open(inbgrcsv, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
      specrows.append(row)

  shp = ogr.Open(inshape)
  lyr = shp.GetLayer()
  numfeat = lyr.GetFeatureCount()

  ## if input image already exists, read it and update,
  ## otherwise, Create output image
  if (os.path.isfile(outimg)):
    outDS = gdal.Open(outimg, gdal.GA_Update)
    band1 = outDS.GetRasterBand(1)  
    band2 = outDS.GetRasterBand(2)  
    band3 = outDS.GetRasterBand(3)  
    blue = band1.ReadAsArray()
    green = band2.ReadAsArray()
    red = band3.ReadAsArray()
  else:
    drv = gdal.GetDriverByName('GTiff')
    outDS = drv.Create(outimg, xsize=inDS.RasterXSize, ysize=inDS.RasterYSize, \
      bands=3, eType=gdal.GDT_Float32, options=["COMPRESS=LZW"])
    outDS.SetProjection(inDS.GetProjection())
    outDS.SetGeoTransform(inDS.GetGeoTransform())
    blue = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.float32)
    green = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.float32)
    red = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.float32)

  ## for each point ASD feature, match the root name to the list and get
  ## Blue, Green, and Red values to insert into the pixel at its location.
  for featnum in range(numfeat):
    feat = lyr.GetNextFeature()
    featname = (feat.GetField("specname"))[0:9]
    geom = feat.GetGeometryRef()
    xval = geom.GetX()
    yval = geom.GetY()
    pix = math.floor((xval - gt[0])/gt[1])
    lin = math.floor((yval - gt[3])/gt[5])
    ## print("%12.2f %12.2f %d %d" % (xval, yval, pix, lin))
    for row in specrows:
      thename = row[0][0:9]
      if(thename == featname):
        blue[lin, pix] = float(row[1])
        green[lin, pix] = float(row[2])
        red[lin, pix] = float(row[3])
        setit = True
        break
      else:
        setit = False

    if (setit == False):
      print("Did not find data for %s" % (featname))
  
  shp, lyr = None, None
         
  print("All point features processed")

  band1 = outDS.GetRasterBand(1)
  band1.SetNoDataValue(0.0)
  band1.WriteArray(blue)
  band2 = outDS.GetRasterBand(2)
  band2.SetNoDataValue(0.0)
  band2.WriteArray(green)
  band3 = outDS.GetRasterBand(3)
  band3.SetNoDataValue(0.0)
  band3.WriteArray(red)
  
  band1, band2, band3 = None, None, None
  inDS, outDS = None, None

if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print("[ ERROR ] you must supply 4 arguments: moorea_grid_asd.py inimgtemplate inbgrcsv inshape outimg")
    print("where:")
    print("    inimgtemplate = the input image whose extent and resolution should be matched.")
    print("    inbgrcsv = the input CSV file with the ASD file names, Blue, Green, and Red data.")
    print("    inshape = the input Shapefile with points for the various spectrometer readings.")
    print("       The point locations were interpolated based on time between segment points.")
    print("    outimg = the output image with the BGR values inserted in the pixels associated with each ASD point.")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )

