#!/bin/env python3
import gdal
import os, sys
import numpy as np
import random
import pyproj

if (len(sys.argv) < 3):
  print('')
  print('extract_big_points.py inimgfile outnpyfile')
  print('')
  sys.exit(0)

infile = sys.argv[1]
outnpy = sys.argv[2]

inDS = gdal.Open(infile, gdal.GA_ReadOnly)
gt = inDS.GetGeoTransform()

## first, read in chunks and determine how many potential points there are
numchunks = int(inDS.RasterYSize//5000 + 1)
chunksizes = np.zeros(numchunks, dtype=np.int) + 5000
if ((inDS.RasterYSize % 5000) > 0):
  chunksizes[-1] = int(inDS.RasterYSize % 5000)
else:
  numchunks -= 1
  chunksizes = chunksizes[0:numchunks]

pointnums = np.zeros(numchunks, dtype=np.int64)

inBand = inDS.GetRasterBand(1)

for i in range(numchunks):
  data = inBand.ReadAsArray(0,i*5000,inDS.RasterXSize, int(chunksizes[i]))
  potent = np.greater(data, 3)
  ## potent = np.greater(data, 1.5)
  pointnums[i] = np.sum(potent)
  del data, potent
  print('Finished Evaluating Chunk %d of %d' % (i+1, numchunks))
  
overall_total = np.sum(pointnums)
print('Overall Total: %d' % (overall_total))

yoffsets = np.roll(np.cumsum(chunksizes), 1)
yoffsets[0] = 0

for i in range(numchunks):
  print('Chunk %d    ChunkSize: %d' % (i+1, chunksizes[i]))
  data = inBand.ReadAsArray(0, int(yoffsets[i]), inDS.RasterXSize, int(chunksizes[i]))
  print('dataSize: %d %d' % data.shape)
  frac = float(pointnums[i])/overall_total
  num = int(np.floor(frac * 20000))
  potent = np.greater(data, 3)
  numpot = np.sum(potent)
  potenty, potentx = np.nonzero(potent)
  if (numpot == 0 or num == 0):
    continue 
  if (numpot > num):
    randit = np.floor(np.random.random_sample(size=num) * numpot).astype(np.int)
  potenty = potenty[randit]
  potentx = potentx[randit]
  vals = data[potenty, potentx]
  del data
  ypseudomerc = ((potenty+yoffsets[i]) * gt[5]) + gt[3]
  xpseudomerc = (potentx * gt[1]) + gt[0]
  del potentx, potenty
  print('Created coordinates for chunk %d' % (i+1))
  ## take randomly selected good index values and reconstruct the pixel and line
  ## to get the EPSG:3857 coordinates and then convert them to lat/lon.
  lon, lat = pyproj.transform(pyproj.Proj(init='epsg:3857'), \
    pyproj.Proj(init='epsg:4326'), xpseudomerc, ypseudomerc)
  satellite_points = np.column_stack((lon, lat, vals))
  if 'final' in locals():
    final = np.append(final, satellite_points, axis=0)
  else:
    final = np.copy(satellite_points)
  np.save(outnpy, final)
  print('Finished Extraction from Chunk %d of %d' % (i+1, numchunks))

np.save(outnpy, final)
inDS, inBand = None, None


