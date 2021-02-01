#!/bin/env python3
import glob
import os, sys

def main(dovedir):
  """This is the main commandline function (list_unique_dates.py) 
   It reads the SR image files in a directory and lists the unique dates in standard output
  """

  imglist = glob.glob(dovedir+'/2*_SR.tif')

  print("Number of images: %d" % (len(imglist)))
  if (len(imglist) == 0):
    print("No images found that match.")
    sys.exit(0)

  newlist = [ os.path.basename(img) for img in imglist ]

  thedates = [ img[0:8] for img in newlist ]
  uniqdates = sorted(list(set(thedates)))
  for thisdate in uniqdates:
    print("%s" % (thisdate))
  
if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print("[ ERROR ] you must supply 1 arguments: list_unique_dates.py dovedir")
    print("    dovedir = directory containing the Dove images (*_SR.tif) to get search for unique dates.")
    print("")

    sys.exit( 0 )

  main(sys.argv[1])
