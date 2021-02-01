#!/usr/bin/env python3
import geojson
import os, sys
import glob

direxp = sys.argv[1]
outfile = sys.argv[2]

listit = glob.glob(direxp)

fout = open(outfile, 'w+')
fout.write('{"type": "FeatureCollection", "features": [')

for k,thisfile in enumerate(listit):
  f = open(thisfile, 'r')
  myjson = geojson.load(f)
  f.close()
  numfeat = len(myjson.features)
  if (k == (len(listit)-1)):
    numfeat -= 1
  count = 0
  for i in range(0, numfeat):
    fout.write(geojson.dumps(myjson[i])+', ')
    count += 1
  if (k == (len(listit)-1)):
    fout.write(geojson.dumps(myjson[numfeat]))
  print('Finished %s: %d' % (thisfile, count))
  
fout.write(']}')
fout.close()
  
