#!/bin/env python3
from Py6S import *
import gdal, osr
import numpy as np
import pyproj
import subprocess
import time
from scipy import interpolate
import mtlutils
import sys, os
  
def main(infile, inaot, inwv, inoz, outputdir):

  metadatafile = infile[:-4] + "_MTL.txt"

  if (os.path.isfile(outputdir+os.sep+os.path.basename(infile).split('.')[0]+"_luts.npz")):
    print(("%s exists, skipping\n") % (outputdir+os.sep+os.path.basename(infile).split('.')[0]+"_luts.npz")) 
    sys.exit(0)

  if (os.path.isfile(infile)):
    try:
      inds = gdal.Open(infile, gdal.GA_ReadOnly)
    except:
      print(("%s could not open.\n") % (infile))
      sys.exit(1)
  else:
    print(("%s file not found.\n") % (infile))
    sys.exit(0)

  metadata = mtlutils.parsemeta(metadatafile)
  mymonth = metadata['L1_METADATA_FILE']['PRODUCT_METADATA']['DATE_ACQUIRED'].month
  myday = metadata['L1_METADATA_FILE']['PRODUCT_METADATA']['DATE_ACQUIRED'].day
  myhour = metadata['L1_METADATA_FILE']['PRODUCT_METADATA']['SCENE_CENTER_TIME'].hour
  myminute = metadata['L1_METADATA_FILE']['PRODUCT_METADATA']['SCENE_CENTER_TIME'].minute
  mysecond = metadata['L1_METADATA_FILE']['PRODUCT_METADATA']['SCENE_CENTER_TIME'].second
  ## get date and time from Planet file name
  ## mymonth = np.int(os.path.basename(infile)[4:6])
  ## myday = np.int(os.path.basename(infile)[6:8])
  ## myhour = np.int(os.path.basename(infile)[9:11])
  ## myminute = np.int(os.path.basename(infile)[11:13])
  ## mysecond = np.int(os.path.basename(infile)[13:15])
  mydechr = myhour + myminute/60.0 + mysecond/3600.0
 
  ## get projection and geotreansform info to determine center longitude and latitude
  ingt = inds.GetGeoTransform()
  centerutm = []
  centerutm.append(ingt[0] + (inds.RasterXSize * ingt[1])/2.)
  centerutm.append(ingt[3] + (inds.RasterYSize * ingt[5])/2.)
 
  projinfo = osr.SpatialReference()
  projinfo.ImportFromWkt(inds.GetProjectionRef())
  projutm = pyproj.Proj(projinfo.ExportToProj4())
  centerlonlat = projutm(centerutm[0], centerutm[1], inverse=True)
 
  radmins = np.zeros(7, dtype=np.float32)
  radmaxs = np.zeros(7, dtype=np.float32)

  gains = []
  offsets = []

  gains.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_1'])
  gains.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_2'])
  gains.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_3'])
  gains.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_4'])
  gains.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_5'])
  gains.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_6'])
  gains.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_7'])
  offsets.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_1'])
  offsets.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_2'])
  offsets.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_3'])
  offsets.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_4'])
  offsets.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_5'])
  offsets.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_6'])
  offsets.append(metadata['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_7'])

  for band in range(inds.RasterCount):
    thisBand = inds.GetRasterBand(band+1).ReadAsArray()
    notzero = np.greater(thisBand, 0)
    radmins[band] = np.min(thisBand[notzero] * gains[band] + offsets[band])
    radmaxs[band] = np.max(thisBand[notzero] * gains[band] + offsets[band])
    print(("Range in Band %d: %d, %d") % (band+1, radmins[band], radmaxs[band]))

  del inds, thisBand

  rangecoast = np.zeros((2, 256), dtype=np.float32)
  rangeblue = np.zeros((2, 256), dtype=np.float32)
  rangegreen = np.zeros((2, 256), dtype=np.float32)
  rangered = np.zeros((2, 256), dtype=np.float32)
  rangenir = np.zeros((2, 256), dtype=np.float32)
  rangeswir1 = np.zeros((2, 256), dtype=np.float32)
  rangeswir2 = np.zeros((2, 256), dtype=np.float32)


  for lev in np.arange(256):
    rangecoast[0, lev] = (lev * (radmaxs[0] - radmins[0])/255. + radmins[0])
    rangeblue[0, lev] = (lev * (radmaxs[1] - radmins[1])/255. + radmins[1])
    rangegreen[0, lev] = (lev * (radmaxs[2] - radmins[2])/255. + radmins[2])
    rangered[0, lev] = (lev * (radmaxs[3] - radmins[3])/255. + radmins[3])
    rangenir[0, lev] = (lev * (radmaxs[4] - radmins[4])/255. + radmins[4])
    rangeswir1[0, lev] = (lev * (radmaxs[5] - radmins[5])/255. + radmins[5])
    rangeswir2[0, lev] = (lev * (radmaxs[6] - radmins[6])/255. + radmins[6])

  print("Running Iterations of Atmos. Correction")

  for lev in np.arange(256):
    ## create command line string
    cmd1 = "sbatch -p SHARED -n 1 --mem=100 rad_level_landsat.py "+infile + ((" %d") % (lev)) + (" %6f") % (rangecoast[0,lev])
    cmd2a = (" %6f") % (rangeblue[0,lev]) + (" %6f") % (rangegreen[0,lev]) + (" %6f") % (rangered[0,lev])
    cmd2b = (" %6f") % (rangenir[0,lev]) + (" %6f") % (rangeswir1[0,lev]) + (" %6f") % (rangeswir2[0,lev])
    cmd3 = " " + inaot + " " + inwv + " " + inoz + (" %d") % (mymonth) + (" %d") % (myday)
    cmd4 = (" %6f") % (mydechr) + (" %8f") % (centerlonlat[0]) + (" %8f") % (centerlonlat[1])
    ## cmd1 = "rad_level.py "+infile + ((" %d") % (lev)) + (" %6f") % (rangeblue[0,lev])
    ## cmd2 = (" %6f") % (rangegreen[0,lev]) + (" %6f") % (rangered[0,lev]) + (" %6f") % (rangenir[0,lev])
    ## cmd3 = " " + inaot + " " + inwv + " " + inoz + (" %d") % (mymonth) + (" %d") % (myday)
    ## cmd4 = (" %6f") % (mydechr) + (" %8f") % (centerlonlat[0]) + (" %8f") % (centerlonlat[1])
    print(cmd1+cmd2a+cmd2b+cmd3+cmd4)
    subprocess.Popen([cmd1+cmd2a+cmd2b+cmd3+cmd4], cwd=outputdir, shell=True)  

  print("Waiting for 3 minutes")
  time.sleep(180.0) 

  print("Iterations Done - Finishing LUT")
  
  for lev in np.arange(256):
    inrefl = np.load(outputdir+os.sep+os.path.basename(infile).split('.')[0]+("_%03d" % lev)+".npy")
    rangecoast[1, lev] = inrefl[0,1] * 10000
    rangeblue[1, lev] = inrefl[1,1] * 10000
    rangegreen[1, lev] = inrefl[2,1] * 10000
    rangered[1, lev] = inrefl[3,1] * 10000
    rangenir[1, lev] = inrefl[4,1] * 10000
    rangeswir1[1, lev] = inrefl[5,1] * 10000
    rangeswir2[1, lev] = inrefl[6,1] * 10000
  
  np.savez(outputdir+os.sep+os.path.basename(infile).split('.')[0][:-4]+"_luts.npz", rangecoast=rangecoast, \
    rangeblue=rangeblue, rangegreen=rangegreen, rangered=rangered, rangenir=rangenir, rangeswir1=rangeswir1, \
    rangeswir2=rangeswir2)
  print("Done!  Luts saved in " + os.path.basename(infile).split('.')[0][:-4]+"_luts.npz")

  ## remove the unneeded files
  for lev in np.arange(256):
    os.remove(outputdir+os.sep+os.path.basename(infile).split('.')[0]+("_%03d" % lev)+".npy")

## ./rad_level.py 20170126_141040_0e2f_3B_AnalyticMS.tif 100 40.0 29.0 15.0 8.0 0.1 3.6 0.9 1 26 14.178 -65.783 17.967


if __name__ == "__main__":

  if len( sys.argv ) != 6:
    print("[ ERROR ] you must supply 4 arguments: generate_rad_to_refl_lut_landsat.py infile inaot inwv inoz outputdir")
    print("    infile = name of input image file to generate LUTS for")
    print("    inaot = input AOT at 550nm")
    print("    inwv = input water vapor")
    print("    inoz = input ozone")
    print("    outputdir = the directory in which output LUT will be placed")
    print("")

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
