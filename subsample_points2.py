#!/usr/bin/env python3
import ogr, osr
import numpy as np
import os, sys
import geojson

inshpfile = sys.argv[1]
outgeojsonfile = sys.argv[2]
numsamps = int(sys.argv[3])
thresh = int(sys.argv[4])

drv = ogr.GetDriverByName('ESRI Shapefile')
siteshp = drv.Open(inshpfile, 0)
lyr = siteshp.GetLayer(0)
featcount = lyr.GetFeatureCount()
sourceSR = lyr.GetSpatialRef()
defn = lyr.GetLayerDefn()

## randvals = np.random.randint(0, featcount, numsamps).tolist()

fout = open(outgeojsonfile, 'w+')
fout.write('{"type": "FeatureCollection", "features": [')

outarr = np.zeros(numsamps, dtype=int)
idarr = np.zeros(numsamps, dtype=int)

count = 0

if (featcount > numsamps):
  while (count < numsamps):
    feat = lyr.GetFeature(np.random.randint(0, featcount))
    b3mean = feat.GetField('B3_mean')
    if (b3mean < thresh):
      continue
    myPoint = geojson.Point(feat.GetGeometryRef().GetPoint_2D())
    myFeat = geojson.Feature(geometry=myPoint, properties={'B3_mean': b3mean})
    fout.write(geojson.dumps(myFeat) + ', ')
    count += 1
else:
  for i in range(featcount):
    feat = lyr.GetFeature(i)
    b3mean = feat.GetField('B3_mean')
    if (b3mean < thresh):
      continue
    myPoint = geojson.Point(feat.GetGeometryRef().GetPoint_2D())
    myFeat = geojson.Feature(geometry=myPoint, properties={'B3_mean': b3mean})
    fout.write(geojson.dumps(myFeat) + ', ')
    count += 1

## close input file
siteshp = None

print('File: %s   Input points: %d   Output points: %d' % (outgeojsonfile, featcount, count))

## close out output file, overwriting last comma and closing brackets, etc.
mypos = fout.tell()
fout.seek(mypos-2)
fout.write(']}')
fout.close()
