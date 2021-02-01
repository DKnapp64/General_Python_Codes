#!/bin/env python3
import numpy as np
import gdal
import os, sys
from rb_hawaii import rb

def main(infile, outfile, chla_global):
  """This is a command line program for quickly getting the depth and bottom reflectance (Rb)
     for an input surface reflectance image.  You must supply the Chl-a concentration.
  """ 

  #depthfile = os.path.splitext(infile)[0] + "_depth.tif"
  depthfile = '/scratch/dknapp4/Hawaii_Weekly/AscendingDescending/Depth/hawaii_sentinel2_depth_tiff.tif'
  #rbfile = os.path.splitext(infile)[0] + "_rb.tif"
  rbfile = outfile

  #try:
  #  depth(infile, chla_global, depthfile, None)
  #except:
  #  print("Error: Could not create Depth data.")

  print(("Processed Depth: %s") % (depthfile))

  if (os.path.isfile(depthfile)):
    try:
      rb(infile, chla_global, depthfile, rbfile, None)
    except:
      print("Error: Could not create Rb data.")
  else:
    print(("Error: Could not find depth data file %s, so could not do bottom reflectance.") % (depthfile))

  print(("Processed Rb: %s") % (rbfile))


if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ USAGE ] you must supply two arguments: depth_rb_noauto_test_sentdepth_hawaii.py infile chla")
    print("     infile: input surface reflectance image to process")
    print("     chl-a: the Chl-a concentration")
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], float(sys.argv[3]) )
