#!/bin/env python3
import gdal
import os, sys
import numpy as np
import pyproj


if (len(sys.argv) < 3):
  if (len(sys.argv) == 2):
    infile = sys.argv[1]
    outnpy = os.path.dirname(sys.argv[1]) + os.path.sep + os.path.splitext(os.path.basename(sys.argv[1]))[0] + '_points.npy'
    if (os.path.dirname(sys.argv[1]) != ''):
      outnpy = os.path.dirname(sys.argv[1]) + os.path.sep + os.path.splitext(os.path.basename(sys.argv[1]))[0] + '_points.npy'
    else:
      outnpy = os.path.splitext(os.path.basename(sys.argv[1]))[0] + '_points.npy'
  else:  
    print('')
    print('extract_points_for_heat.py intiffile outnpyfile')
    print('')
    sys.exit(0)
else:
  infile = sys.argv[1]
  outnpy = sys.argv[2]

inDS = gdal.Open(infile, gdal.GA_ReadOnly)
gt = inDS.GetGeoTransform()

inBand = inDS.GetRasterBand(1)
data = inBand.ReadAsArray()
inDS = None

good = np.greater_equal(data, 3)
numgood = np.sum(good)
if (numgood == 0):
  sys.exit(0)

print('Good Pixels above or equal to 3: %d' % (numgood))
## np.save('combo_temp_aboveeq3.npy', good)
## good = np.load('combo_above4.npy')
## index = np.arange(0,inDS.RasterXSize * inDS.RasterYSize)
xcoord = gt[0]
ycoord = gt[3]

index0, index1 = np.nonzero(good)
## np.save('index0_temp.npy', index0)
## np.save('index1_temp.npy', index1)

print('Made index')

## randomly select 20000 points, since that is the limit that
## the Google Maps heatmap function can accept.
if (numgood > 1000):
  randit = np.round(np.random.random_sample(size=1000) * (numgood-1)).astype(np.int)
  print('Selected down index')
  newindex0 = index0[randit]
  newindex1 = index1[randit]
  print('Selected down randomly')
else:
  newindex0 = index0.copy()
  newindex1 = index1.copy()

perdevvals = data[newindex0, newindex1]
del data, index0, index1

ypseudomerc = (newindex0 * gt[5]) + gt[3]
xpseudomerc = (newindex1 * gt[1]) + gt[0]

print('Created Pseudo-Mercator coordinates')
## take randomly selected good index values and reconstruct the pixel and line
## to get the EPSG:3857 coordinates and then convert them to lat/lon.

## convert pseudo-mercator coordinates to latitude-longitude
lon, lat = pyproj.transform(pyproj.Proj(init='epsg:3857'), pyproj.Proj(init='epsg:4326'), xpseudomerc, ypseudomerc)

## stack teh columns together to make a 3-column array of up to 20000 points
satellite_points = np.column_stack((lon, lat, perdevvals))

## save output to an npy file
np.save(outnpy, satellite_points)
