#!/bin/env python2
import numpy as np
import gdal, ogr, osr
from gdalconst import *
from scipy.interpolate import interp1d
import sys
import matplotlib.pyplot as plt
## import pdb

def main( inoutfile, redadj, greenadj, blueadj):
  
  ########################################################
  # Open data
  ########################################################

  ds1 = gdal.Open(inoutfile, GA_Update)
  
  ## get data type

  redadj = np.int(redadj)
  redBand = ds1.GetRasterBand(1)
  thisArray = redBand.ReadAsArray()
  zero = np.equal(thisArray, 0)
  newArray = thisArray + np.float(redadj)
  lesszero = np.less_equal(newArray, 0)
  great255 = np.greater(newArray, 255)
  newArray[lesszero] = 0
  newArray[great255] = 255
  newArray[zero] = 0
  redBand.WriteArray(newArray.astype(np.uint8))
  redBand.FlushCache()
  redBand = None

  greenadj = np.int(greenadj)
  greenBand = ds1.GetRasterBand(2)
  thisArray = greenBand.ReadAsArray()
  zero = np.equal(thisArray, 0)
  newArray = thisArray + np.float(greenadj)
  lesszero = np.less_equal(newArray, 0)
  great255 = np.greater(newArray, 255)
  newArray[lesszero] = 0
  newArray[great255] = 255
  newArray[zero] = 0
  greenBand.WriteArray(newArray.astype(np.uint8))
  greenBand.FlushCache()
  greenBand = None

  blueadj = np.int(blueadj)
  blueBand = ds1.GetRasterBand(3)
  thisArray = blueBand.ReadAsArray()
  zero = np.equal(thisArray, 0)
  newArray = newArray + np.float(blueadj)
  lesszero = np.less_equal(newArray, 0)
  great255 = np.greater(newArray, 255)
  newArray[lesszero] = 0
  newArray[great255] = 255
  newArray[zero] = 0
  blueBand.WriteArray(newArray.astype(np.uint8))
  blueBand.FlushCache()
  blueBand = None
 
  ds1 = None
  
if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print "[ USAGE ] you must supply 4 arguments: bright_adjust_diumac.py inoutdimac redadj greenadj blueadj"
    print ""
    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )

