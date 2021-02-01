#!/bin/env python
import numpy as np
import gdal
import os, sys
from rb_hawaii import rb

def main(infile, outfile, depthfile, chla_global):
  rbfile = outfile

  print(("Input Depth: %s") % (depthfile))

  if (os.path.isfile(depthfile)):
    try:
      rb(infile, chla_global, depthfile, rbfile, None)
    except:
      print("Error: Could not create Rb data.")
  else:
    print(("Error: Could not find depth data file %s, so could not do bottom reflectance.") % (depthfile))

  print(("Processed Rb: %s") % (rbfile))


if __name__ == "__main__":
  if len( sys.argv ) != 5:
    print("[ USAGE ] you must supply two arguments: depth_rb_noauto_hawaii_test.py infile outfile depthfile chla")
    print("     infile: input surface reflectance image to process")
    print("     outfile: output bottom reflectance image to process")
    print("     depthfile: input depthfile to use")
    print("     chl-a: the Chl-a concentration")
    sys.exit( 0 )
  main( sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]) )
