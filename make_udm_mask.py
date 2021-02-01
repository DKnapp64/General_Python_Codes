import gdal
import numpy as np
import os, sys

def make_udm_mask(maskfile):
  try:
    inDS = gdal.Open(maskfile, gdal.GA_ReadOnly)
  except:
    print(("Error: Could not open file %s") % (maskfile)) 

  b1 = inDS.GetRasterBand(1).ReadAsArray()
  b7 = inDS.GetRasterBand(7).ReadAsArray()
  goodmask = np.logical_and(np.equal(b1, 1), np.greater(b7, 75))
  inDS = None
  return goodmask
    
