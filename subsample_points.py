#!/usr/bin/env python3
import ogr, osr
import numpy as np
import os, sys
import geojson

inshpfile = sys.argv[1]
outgeojsonfile = sys.argv[2]
numsamps = int(sys.argv[3])

drv = ogr.GetDriverByName('ESRI Shapefile')
siteshp = drv.Open(inshpfile, 0)
lyr = siteshp.GetLayer(0)
featcount = lyr.GetFeatureCount()
sourceSR = lyr.GetSpatialRef()
defn = lyr.GetLayerDefn()

randvals = np.random.randint(0, featcount, numsamps).tolist()

fout = open(outgeojsonfile, 'w+')
fout.write('{"type": "FeatureCollection", "features": [')

count = 0

for i in randvals:
  feat = lyr.GetFeature(i)
  myPoint = geojson.Point(feat.GetGeometryRef().GetPoint_2D())
  b3mean = feat.GetField('B3_mean')
  myFeat = geojson.Feature(geometry=myPoint, properties={'B3_mean': b3mean})
  fout.write(geojson.dumps(myFeat) + ', ')
  count += 1


## close input file
siteshp = None

print('Input points: %d   Output points: %d' % (featcount, count))

## clous out output file, overwriting last comma and closing brackets, etc.
mypos = fout.tell()
fout.seek(mypos-2)
fout.write(']}')
fout.close()
