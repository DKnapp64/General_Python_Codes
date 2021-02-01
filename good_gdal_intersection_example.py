#!/usr/bin/env pythnon2
import gdal, osr
import numpy as np
import sys, os
## import pdb

image1 = 'ecuador_global_acd'
image2 = 'peru_acd.tif'

img1 = gdal.Open(image1)
img2 = gdal.Open(image2)

gt2 = img2.GetGeoTransform()

osr18 = osr.SpatialReference()
osr18.ImportFromEPSG(32718)
osr17 = osr.SpatialReference()
osr17.ImportFromEPSG(32717)

tx = osr.CoordinateTransformation(osr17, osr18)
g = gdal.Open(image1)
gt1 = g.GetGeoTransform()
x_size = g.RasterXSize
y_size = g.RasterYSize

(ulx, uly, ulz) = tx.TransformPoint( gt1[0], gt1[3])
(lrx, lry, lrz) = tx.TransformPoint( gt1[0]+gt1[1]*x_size, \
                                     gt1[3]+gt1[5]*y_size)

mem_drv = gdal.GetDriverByName('MEM')

dest = mem_drv.Create('', int((lrx-ulx)/gt2[1]), \
        int((uly-lry)/np.abs(gt2[5])), 1, gdal.GDT_Float32)

new_geo = (ulx, gt2[1], gt1[2], \
           uly, gt1[4], gt2[5])

dest.SetGeoTransform(new_geo)
dest.SetProjection(osr17.ExportToWkt())

res = gdal.ReprojectImage(g, dest, \
        osr17.ExportToWkt(), osr18.ExportToWkt(), \
        gdal.GRA_NearestNeighbour)

## find bounds of images
r1 = [new_geo[0], new_geo[3], new_geo[0] + (new_geo[1] * dest.RasterXSize), new_geo[3] + (new_geo[5] * dest.RasterYSize)]
r2 = [gt2[0], gt2[3], gt2[0] + (gt2[1] * img2.RasterXSize), gt2[3] + (gt2[5] * img2.RasterYSize)]

## find intersection
intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]

if r1 != r2:
  print '\t** different bounding boxes **'
  # check for any overlap
  print '\tintersection:',intersection
  left1 = int(round((intersection[0]-r1[0])/new_geo[1])) # difference divided by pixel dimension
  top1 = int(round((intersection[1]-r1[1])/new_geo[5]))
  col1 = int(round((intersection[2]-r1[0])/new_geo[1])) - left1 # difference minus offset left
  row1 = int(round((intersection[3]-r1[1])/new_geo[5])) - top1
  
  left2 = int(round((intersection[0]-r2[0])/gt2[1])) # difference divided by pixel dimension
  top2 = int(round((intersection[1]-r2[1])/gt2[5]))
  col2 = int(round((intersection[2]-r2[0])/gt2[1])) - left2 # difference minus new left offset
  row2 = int(round((intersection[3]-r2[1])/gt2[5])) - top2
  
  #print '\tcol1:',col1,'row1:',row1,'col2:',col2,'row2:',row2
  if col1 != col2 or row1 != row2:
      print "*** MEGA ERROR *** COLS and ROWS DO NOT MATCH ***"
  # these arrays should now have the same spatial geometry though NaNs may differ
  array1 = dest.ReadAsArray(left1,top1,col1,row1)
  array2 = img2.ReadAsArray(left2,top2,col2,row2)

  good = np.logical_and(np.greater(array1, 0.0), np.greater(array2, 0.0))

  print("Number of Good pixels: %d" % good.sum())

  combined = np.vstack((array1[good], array2[good])).T

  np.save('combined_data.npy', combined)

del img1, img2, dest
