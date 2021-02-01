#!/bin/env python3
import numpy as np
import geojson
import glob
import os, sys

## gather points for a given date
## 20190806 20190813 20190820 20190827 20190903 20190910 20190917
## 20190924 20191001 20191008 20191015 20191022 20191029 20191105
  
def main(indate, outfile):
  
  listfiles = glob.glob('*_points.npy')
  weekpoints = []
  
  for infile in listfiles:
    if (infile.find(indate) != -1):
      weekpoints.append(infile)
  
  fout = open(outfile, 'w+')
  fout.write('{"type": "FeatureCollection", "features": [')
  
  for thisfile in weekpoints:
    indata = np.load(thisfile)
    above2 = np.greater(indata[:,2], 2)
    print('%d' % (indata.shape[0]))
    indata = indata[above2,:]
    print('%d' % (indata.shape[0]))
    for row in range(indata.shape[0]):
      thisPoint = geojson.Point((indata[row,0], indata[row,1])) 
      thisFeature = geojson.Feature(geometry=thisPoint, properties={"Count": indata[row,2]}) 
      mydumps = geojson.dumps(thisFeature)
      fout.write(mydumps+', ')
  
  ##   thisPoint = geojson.Point((indata[-1,0], indata[-1,1]))
  ##   thisFeature = geojson.Feature(geometry=thisPoint, properties={"Count": indata[-1,2]}) 
  ##   mydumps = geojson.dumps(thisFeature)
  ##   fout.write(mydumps+', ')
  
  mypos = fout.tell()
  print(mypos)
  fout.seek(mypos-2)
  fout.write(']}')
  fout.close()


if __name__ == "__main__":
  if (len(sys.argv) != 3):
    print( "Usage: join_points.py DATE outfile")
    sys.exit(0)
  main( sys.argv[1], sys.argv[2] )
