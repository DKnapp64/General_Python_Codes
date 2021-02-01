#!/bin/env python3
from Py6S import *
import gdal, osr
import numpy as np
import pyproj
import subprocess
import time
from scipy import interpolate
import sys, os
  
def main(infile, inaot, inwv, inoz, outputdir):

  inds = gdal.Open(infile, gdal.GA_ReadOnly)
  
  ## get date and time from Planet file name
  mymonth = np.int(os.path.basename(infile)[4:6])
  myday = np.int(os.path.basename(infile)[6:8])
  myhour = np.int(os.path.basename(infile)[9:11])
  myminute = np.int(os.path.basename(infile)[11:13])
  mysecond = np.int(os.path.basename(infile)[13:15])
  mydechr = myhour + myminute/60.0 + mysecond/3600.0
  mysatid = np.int(os.path.basename(infile)[19:20])
 
  ## get projection and geotreansform info to determine center longitude and latitude
  ingt = inds.GetGeoTransform()
  centerutm = []
  centerutm.append(ingt[0] + (inds.RasterXSize * ingt[1])/2.)
  centerutm.append(ingt[3] + (inds.RasterYSize * ingt[5])/2.)
 
  projinfo = osr.SpatialReference()
  projinfo.ImportFromWkt(inds.GetProjectionRef())
  projutm = pyproj.Proj(projinfo.ExportToProj4())
  centerlonlat = projutm(centerutm[0], centerutm[1], inverse=True)
 
  radmins = np.zeros(4, dtype=np.float32)
  radmaxs = np.zeros(4, dtype=np.float32)

  for band in range(inds.RasterCount):
    thisBand = inds.GetRasterBand(band+1).ReadAsArray()
    notzero = np.greater(thisBand, 0)
    radmins[band] = np.min(thisBand[notzero])
    radmaxs[band] = np.max(thisBand[notzero])
    print(("Range in Band %d: %d, %d") % (band+1, radmins[band], radmaxs[band]))

  del inds, thisBand

  rangeblue = np.zeros((2, 256), dtype=np.float32)
  rangegreen = np.zeros((2, 256), dtype=np.float32)
  rangered = np.zeros((2, 256), dtype=np.float32)
  rangenir = np.zeros((2, 256), dtype=np.float32)

  for lev in np.arange(256):
    rangeblue[0, lev] = (lev * (radmaxs[0] - radmins[0])/255. + radmins[0]) * 0.01
    rangegreen[0, lev] = (lev * (radmaxs[1] - radmins[1])/255. + radmins[1]) * 0.01
    rangered[0, lev] = (lev * (radmaxs[2] - radmins[2])/255. + radmins[2]) * 0.01
    rangenir[0, lev] = (lev * (radmaxs[3] - radmins[3])/255. + radmins[3]) * 0.01

  print("Running Iterations of Atmos. Correction")

  for lev in np.arange(256):
    ## create command line string
    cmd1 = "srun -p DGE -n 1 rad_level_skysat.py "+infile + ((" %d") % (mysatid)) + ((" %d") % (lev)) + (" %6f") % (rangeblue[0,lev])
    cmd2 = (" %6f") % (rangegreen[0,lev]) + (" %6f") % (rangered[0,lev]) + (" %6f") % (rangenir[0,lev])
    cmd3 = " " + inaot + " " + inwv + " " + inoz + (" %d") % (mymonth) + (" %d") % (myday)
    cmd4 = (" %6f") % (mydechr) + (" %8f") % (centerlonlat[0]) + (" %8f") % (centerlonlat[1])
    ## cmd1 = "./rad_level.py "+infile + ((" %d") % (lev)) + (" %6f") % (rangeblue[0,lev])
    ## cmd2 = (" %6f") % (rangegreen[0,lev]) + (" %6f") % (rangered[0,lev]) + (" %6f") % (rangenir[0,lev])
    ## cmd3 = " " + inaot + " " + inwv + " " + inoz + (" %d") % (mymonth) + (" %d") % (myday)
    ## cmd4 = (" %6f") % (mydechr) + (" %8f") % (centerlonlat[0]) + (" %8f") % (centerlonlat[1])
    print(cmd1+cmd2+cmd3+cmd4)
    subprocess.Popen([cmd1+cmd2+cmd3+cmd4], cwd=outputdir, shell=True)  
    time.sleep(1.0) 

  print("Waiting for 1 minute")
  time.sleep(60.0) 

  print("Iterations Done - Finishing LUT")
  
  for lev in np.arange(256):
    inrefl = np.load(outputdir+os.path.basename(infile).split('.')[0]+("_%03d" % lev)+".npy")
    rangeblue[1, lev] = inrefl[0] * 10000
    rangegreen[1, lev] = inrefl[1] * 10000
    rangered[1, lev] = inrefl[2] * 10000
    rangenir[1, lev] = inrefl[3] * 10000
  
  np.savez(outputdir+os.path.basename(infile).split('.')[0]+"_luts.npz", rangeblue=rangeblue, rangegreen=rangegreen, rangered=rangered, rangenir=rangenir)
  print("Done!  Luts saved in " + os.path.basename(infile).split('.')[0]+"_invar_luts.npz")

  ## remove the unneeded files
  for lev in np.arange(256):
    os.remove(outputdir+os.path.basename(infile).split('.')[0]+("_%03d" % lev)+".npy")

## ./rad_level.py 20170126_141040_0e2f_3B_AnalyticMS.tif 100 40.0 29.0 15.0 8.0 0.1 3.6 0.9 1 26 14.178 -65.783 17.967


if __name__ == "__main__":

  if len( sys.argv ) != 6:
    print("[ ERROR ] you must supply 4 arguments: generate_rad_to_refl_lut.py infile inaot inwv inoz outputdir")
    print("    infile = name of input image file to generate LUTS for")
    print("    inaot = input AOT at 550nm")
    print("    inwv = input water vapor")
    print("    inoz = input ozone")
    print("    outputdir = the directory in which output LUT will be placed")
    print("")

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
