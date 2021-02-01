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
  
  tabdata = np.genfromtxt(inbgrcsv, dtype=[('names', '|S43'), ('blue', 'f8'), ('green', 'f8'), 
    ('red', 'f8')], delimiter=',', skip_header=0)

  tabnames = np.chararray(len(tabdata), itemsize=10) 
  for d in range(len(tabdata)):
    tabnames[d] = tabdata['names'][d][0:9] 

  newstuff = np.zeros((2, len(tabdata)), dtype=np.int64)

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
    band4 = outDS.GetRasterBand(4)  
    band5 = outDS.GetRasterBand(5)  
    band6 = outDS.GetRasterBand(6)  
    blue = band1.ReadAsArray()
    green = band2.ReadAsArray()
    red = band3.ReadAsArray()
    bluesd = band4.ReadAsArray()
    greensd = band5.ReadAsArray()
    redsd = band6.ReadAsArray()
  else:
    drv = gdal.GetDriverByName('GTiff')
    outDS = drv.Create(outimg, xsize=inDS.RasterXSize, ysize=inDS.RasterYSize, \
      bands=inDS.RasterCount * 2, eType=gdal.GDT_Float32, options=["COMPRESS=LZW"])
    outDS.SetProjection(inDS.GetProjection())
    outDS.SetGeoTransform(inDS.GetGeoTransform())
    blue = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.float32)
    green = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.float32)
    red = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.float32)
    bluesd = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.float32)
    greensd= np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.float32)
    redsd= np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.float32)

  ## for each point ASD feature, match the root name to the list and get
  ## Blue, Green, and Red values to insert into the pixel at its location.

  pix = np.zeros(numfeat, dtype=np.int64)
  lin = np.zeros(numfeat, dtype=np.int64)
  textit = np.chararray(numfeat, itemsize=11)

  featnames = []

  for featnum in range(numfeat):
    feat = lyr.GetNextFeature()
    featnames.append((feat.GetField("specname"))[0:9])
    geom = feat.GetGeometryRef()
    xval = geom.GetX()
    yval = geom.GetY()
    pix[featnum] = math.floor((xval - gt[0])/gt[1])
    lin[featnum] = math.floor((yval - gt[3])/gt[5])
    textit[featnum] = ("%05d %05d" % (pix[featnum], lin[featnum]))

  uniqrowcol, uniqind = np.unique(textit, return_index=True)

  templist = []

  for t,k in enumerate(uniqrowcol.tolist()):
    pixlin = [int(k.split()[0].decode()), int(k.split()[1].decode())]
    ## ind = np.logical_and(np.equal(pix, pixlin[0]), np.equal(lin, pixlin[1]))
    ## numvals = ind.sum()
    print(pixlin)
    set1 = np.char.equal(k, textit)
    setfeatnames = np.asarray(featnames)[set1]
    pixlistblue = []    
    pixlistgreen = []    
    pixlistred = []    

    for thename in setfeatnames.tolist():
      for j,tabrow in enumerate(tabnames):
        if (tabrow.decode() == thename):
          pixlistblue.append(tabdata['blue'][j])
          pixlistgreen.append(tabdata['green'][j])
          pixlistred.append(tabdata['red'][j])
          break

    print(k, len(pixlistblue))
    meanvalblue = np.mean(np.asarray(pixlistblue))
    sdvalblue = np.std(np.asarray(pixlistblue))
    meanvalgreen = np.mean(np.asarray(pixlistgreen))
    sdvalgreen = np.std(np.asarray(pixlistgreen))
    meanvalred = np.mean(np.asarray(pixlistred))
    sdvalred = np.std(np.asarray(pixlistred))
    blue[pixlin[1], pixlin[0]] = meanvalblue
    green[pixlin[1], pixlin[0]] = meanvalgreen
    red[pixlin[1], pixlin[0]] = meanvalred
    bluesd[pixlin[1], pixlin[0]] = sdvalblue
    greensd[pixlin[1], pixlin[0]] = sdvalgreen
    redsd[pixlin[1], pixlin[0]] = sdvalred

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
  band4 = outDS.GetRasterBand(4)
  band4.SetNoDataValue(0.0)
  band4.WriteArray(bluesd)
  band5 = outDS.GetRasterBand(5)
  band5.SetNoDataValue(0.0)
  band5.WriteArray(greensd)
  band6 = outDS.GetRasterBand(6)
  band6.SetNoDataValue(0.0)
  band6.WriteArray(redsd)
  
  band1, band2, band3, band4, band5, band6 = None, None, None, None, None, None
  inDS, outDS = None, None

if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print("[ ERROR ] you must supply 4 arguments: moorea_grid_avg_asd.py inimgtemplate inbgrcsv inshape outimg")
    print("where:")
    print("    inimgtemplate = the input image whose extent and resolution should be matched.")
    print("    inbgrcsv = the input CSV file with the ASD file names, Blue, Green, and Red data.")
    print("    inshape = the input Shapefile with points for the various spectrometer readings.")
    print("       The point locations were interpolated based on time between segment points.")
    print("    outimg = the output image with the BGR values inserted in the pixels associated with each ASD point.")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )

