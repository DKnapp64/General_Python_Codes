#!/usr/bin/env python3
import geojson
import os, sys
import glob

direxp = sys.argv[1]
outfile = sys.argv[2]
thresh = int(sys.argv[3])

listit = glob.glob(direxp)

fout = open(outfile, 'w+')
fout.write('{"type": "FeatureCollection", "features": [')

total = 0

for thisfile in listit:
  f = open(thisfile, 'r')
  myjson = geojson.load(f)
  f.close()
  numfeat = len(myjson.features)
  count = 0
  for i in range(0, numfeat-1):
    if (myjson[i]['properties']['Count'] >= thresh):
      fout.write(geojson.dumps(myjson[i])+', ')
      count += 1
      total += 1
    else:
      continue
  print('Finished %s: %d' % (thisfile, count))

fout.write(']}')
fout.close()

print('Total Points: %d' % (total))
  
  
