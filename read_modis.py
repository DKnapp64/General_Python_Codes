#!/bin/env python3
import gdal
import osr
import numpy as np
import os, sys
import glob
import copy

def modclear(apix, bpix):
  binpix = bin(apix)
  ## identify pixels that have a cloud_state of "clear", have no cloud_shadow, 
  ## and have cirrus_detected value of "none"
  if ((int(binpix[-2:]) == 0) and (int(binpix[-3]) == 0) and (int(binpix[-9:-7]) > 2) and (bpix != -28672)):
    return True

def main(indir, hvtile, outimgfile):
  ## infile = "MOD09A1.A2018353.h09v08.006.2019032175526.hdf"
  ##inlist = [infile]
  inlist = glob.glob(indir+os.path.sep+"MOD09A1.*"+hvtile+"*.hdf")
  
  inlist.sort()

  print("Files for tile %s: %d" % (hvtile, len(inlist)))
  nullit = [ print("%s" % (os.path.basename(thefile))) for thefile in inlist ]
  
  for j,thename in enumerate(inlist):
    ## get list of subdatasets
    tmpDS = gdal.Open(thename, gdal.GA_ReadOnly)
    subdatasets = tmpDS.GetSubDatasets()
    blueband = subdatasets[2][0]
    greenband = subdatasets[3][0]
    redband = subdatasets[0][0]
    nirband = subdatasets[1][0]
    qcband = subdatasets[7][0]
    tmpDS = None
  
    inBlue = gdal.Open(blueband, gdal.GA_ReadOnly)
    inGreen = gdal.Open(greenband, gdal.GA_ReadOnly)
    inRed = gdal.Open(redband, gdal.GA_ReadOnly)
    inNIR = gdal.Open(nirband, gdal.GA_ReadOnly)
    inQA = gdal.Open(qcband, gdal.GA_ReadOnly)
  
    newBlue = inBlue.GetRasterBand(1).ReadAsArray()
    newGreen = inGreen.GetRasterBand(1).ReadAsArray()
    newRed = inRed.GetRasterBand(1).ReadAsArray()
    newNIR = inNIR.GetRasterBand(1).ReadAsArray()
    newQA = inQA.GetRasterBand(1).ReadAsArray()
  
    if (j == 0):
      datatype = inBlue.GetRasterBand(1).DataType
      currBlue = copy.deepcopy(newBlue)
      currGreen = copy.deepcopy(newGreen)
      currRed = copy.deepcopy(newRed)
      currNIR = copy.deepcopy(newNIR)
      currQA = copy.deepcopy(newQA)
      oldBlue = copy.deepcopy(newBlue)
      oldGreen = copy.deepcopy(newGreen)
      oldRed = copy.deepcopy(newRed)
      oldNIR = copy.deepcopy(newNIR)
      oldQA = copy.deepcopy(newQA)
      inBlue, inGreen, inRed, inNIR, inQA = None, None, None, None, None
      continue
  
    gt = inBlue.GetGeoTransform()
    srs = inBlue.GetProjectionRef()
  
    good = np.vectorize(modclear, otypes=[bool])(newQA, newBlue)
    currBlue[good] = newBlue[good]
    currGreen[good] = newGreen[good]
    currRed[good] = newRed[good]
    currNIR[good] = newNIR[good]
    currQA[good] = newQA[good]
  
  drv = gdal.GetDriverByName('GTiff')
  outDS = drv.Create(outimgfile, currBlue.shape[1], currBlue.shape[0], 4, datatype)
  outDS.SetGeoTransform(gt)
  outDS.SetProjection(srs)
  outDS.GetRasterBand(1).WriteArray(currBlue)
  outDS.GetRasterBand(2).WriteArray(currGreen)
  outDS.GetRasterBand(3).WriteArray(currRed)
  outDS.GetRasterBand(4).WriteArray(currNIR)
  outDS.FlushCache()
  
  outDS = None

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ ERROR ] you must supply 3 arguments: compile_modis.py indir tilestring outimgfile")
    print("where:")
    print("    indir = the input directory with the MODIS MOD09A1 HDF files to composite.")
    print("    tilestring = the tile string to composite (example: h08v06).")
    print("    outimg = the output image with thecompsited Blue, Green, Red, and NIR data (in that order) in GeoTiff format.")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3] )

