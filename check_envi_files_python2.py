#!/usr/bin/python

import sys, getopt
import numpy as np
from osgeo import gdal

def main(argv):

  inputfile = ''
  outputfile = ''

  try:
    inputfile = argv[0]
    outputfile = argv[1]
    print inputfile
    print outputfile
  except:
    print 'Commandname infile outfile'
    sys.exit(2)

  with open(inputfile, 'r') as f:
    lines = f.read().splitlines()

  f.close()

  fout = open(outputfile, 'w')

  for idx, imagefile in enumerate(lines):
    try: 
      ds = gdal.Open(imagefile)
      myarray = np.array(ds.GetRasterBand(1).ReadAsArray())
      minval = myarray.min()
      maxval = myarray.max()
      fout.write(("%s, %f, %f\n") % (imagefile, minval, maxval))
      fout.flush()
      ds = None
    except:
      fout.write(("%s, %s, %s\n") % (imagefile, 'Failed_to_open', 'Failed_to_open'))
      
    if ((idx % 200) == 0):
      print(("Finished %d of %d\n") % (idx, len(lines)))
      fout.flush()
  
  fout.close()

if __name__ == "__main__":
  main(sys.argv[1:])
