#!/bin/env python3
import numpy as np
import gdal
from tempfile import mkdtemp
import scipy.ndimage as s
from skimage.morphology import disk
from skimage.morphology import binary_erosion
from skimage.filters.rank import median
from skimage.measure import label
import shutil
import os, sys
from myrgb2hsv import myrgb2hsv
from getchla import getchla
from depth import depth
from rb import rb

def main(inlistrefl):
  """This is the main commandline program.  It takes a text list of the surface reflectance Planet Dove mosaic tiles 
  (ls -1 L*.tif > inlistrefl.txt).  The tiles are run to infer the Chl-a value.  After removing spurious Chl-a values, 
  the average Chl-a of the tiles is used for all of the tiles that are processed in this batch.  That Clh-a value is 
  then used in the subsequent depth and bottom reflectance steps.
  """ 

  with open(inlistrefl, 'r') as f:
    templist = f.readlines()

  inlist = []
  for thisfile in templist:
    inlist.append(thisfile.strip())

  del templist

  chlavals = np.zeros(len(inlist), dtype=np.float32)

  for k,infile in enumerate(inlist):
    outhsvfile = os.path.splitext(os.path.basename(infile.strip()))[0]+'_hsv'  
    myrgb2hsv(infile, outhsvfile) 
    print(("Processed RGB to HSV: %s") % (infile))
    chlavals[k] = getchla(outhsvfile, infile)
    print(("Chla: %7.4f for %s") % (chlavals[k], infile))
    if (os.path.isfile(outhsvfile)):
      os.remove(outhsvfile)
    if (os.path.isfile(outhsvfile+".hdr")):
      os.remove(outhsvfile+".hdr")

  ## filter out an Nans, negatives and values > 1.0 to get valid Chl-a values
  good1 = np.less(chlavals, 1.0)
  good2 = np.greater(chlavals, 0.0)
  good3 = np.logical_not(np.isnan(chlavals))
  goodchla = np.all(np.stack((good1, good2, good3)), axis=0)

  try:
    chla_global = np.nanmean(chlavals[goodchla])
  except ValueError:
    print("Problem with values in Chl-a array.")

  print(("\nMean Chla for: %7.4f\n") % (chla_global))

  ## process the files to Depth and bottom reflectance using the global Chl-a value
  for k,infile in enumerate(inlist):
    depthfile = os.path.splitext(infile)[0] + "_depth.tif"
    rbfile = os.path.splitext(infile)[0] + "_rb.tif"
    try:
      depth(infile, chla_global, depthfile)
    except:
      print("Error: Could not create Depth data.")
      continue

    print(("Processed Depth: %s") % (depthfile))

    if (os.path.isfile(depthfile)): 
      try:
        rb(infile, chla_global, depthfile, rbfile)
      except:
        print("Error: Could not create Rb data.")
        continue
    else: 
      print(("Error: Could not find depth data file %s, so could not do bottom reflectance.") % (depthfile))
      continue
        
    print(("Processed Rb: %s, %d of %d") % (infile, k, len(inlist)))

  print(("All tiles done!"))

if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print("[ USAGE ] you must supply one argument: preprocess_coral_atlas.py inlistrefl")
    print("     inlistrefl: the text list of the input Planet Dove normalized surface reflectance tiles to process")
    sys.exit( 0 )

  main( sys.argv[1] )
