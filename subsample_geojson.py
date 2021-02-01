#!/usr/bin/env python3
import geojson
import os, sys

infile = sys.argv[1]
outfile = sys.argv[2]
sampstep = int(sys.argv[3])

f = open(infile, 'r')
fout = open(outfile, 'w+')

myjson = geojson.load(f)
f.close()

fout.write('{"type": "FeatureCollection", "features": [')

numfeat = len(myjson.features)

count = 0

for i in range(0, numfeat-1, sampstep):
    myjson[i]["properties"]["Count"] = 1
    fout.write(geojson.dumps(myjson[i])+', ')
    count += 1

print('Input points: %d   Output points: %d' % (numfeat, count))

mypos = fout.tell()                                                             
fout.seek(mypos-2)                                                              
fout.write(']}')                                                                
fout.close()

