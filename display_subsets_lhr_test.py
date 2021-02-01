#!/bin/env python3
import gdal, ogr, osr
import numpy as np
import matplotlib.pyplot as plt
import scipy.misc as sp
import sys, os
import utm
import csv

def close_event():
  plt.close()


def get_overlap_info(focal_bounds, focal_res, img_bounds, img_res):

  ##                X_min      X_max     Y_min     Y_max
  ## Bounding Box: 436933.02 449804.48 1922102.98 1928663.29 
  ## find bounds of images
  ## r1 = [new_geo[0], new_geo[3], new_geo[0] + (new_geo[1] * dest.RasterXSize), new_geo[3] + (new_geo[5] * dest.RasterYSize)]
  ## r2 = [gt2[0], gt2[3], gt2[0] + (gt2[1] * img2.RasterXSize), gt2[3] + (gt2[5] * img2.RasterYSize)]
 
  r1 = [focal_bounds[0], focal_bounds[3], focal_bounds[1], focal_bounds[2]]
  r2 = [img_bounds[0], img_bounds[3], img_bounds[1], img_bounds[2]]
  ## find intersection
  intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]
  ## pdb.set_trace() 
  ## testx = intersection[3]-intersection[0]
  ## testy = intersection[3]-intersection[0]

  # check for any overlap
  left1flt = (intersection[0]-r1[0])/focal_res # difference divided by pixel dimension
  left1 = int(np.abs(round((intersection[0]-r1[0])/focal_res))) # difference divided by pixel dimension
  top1flt = (intersection[1]-r1[1])/focal_res
  top1 = int(np.abs(round(((intersection[1]-r1[1])/focal_res))))
  col1 = int(np.abs(round(((intersection[2]-r1[0])/focal_res) - left1flt))) # difference minus offset left
  row1 = int(np.abs(round(((intersection[3]-r1[1])/focal_res) - top1flt)))
 
  left2flt = (intersection[0]-r2[0])/img_res # difference divided by pixel dimension
  left2 = int(np.abs(round(((intersection[0]-r2[0])/img_res)))) # difference divided by pixel dimension
  top2flt = (intersection[1]-r2[1])/img_res
  top2 = int(np.abs(round(((intersection[1]-r2[1])/img_res))))
  col2 = int(np.abs(round(((intersection[2]-r2[0])/img_res) - left2flt))) # difference minus new left offset
  row2 = int(np.abs(round(((intersection[3]-r2[1])/img_res) - top2flt)))
 
  ## print("%d   %d    %d   %d" % (left1,top1,col1,row1))
  ## print("%d   %d    %d   %d" % (left2,top2,col2,row2))

  return((left1,top1,col1,row1), (left2,top2,col2,row2))
 

input_zone_polygon = 'lhr_test.shp'
csvfile = "lhr_test_sorted_list_cleaned2.txt"

rootDir = "/Carnegie/DGE/CAO/caodata/Scratch/dknapp/Planet/LHR_Test/"

imglist = np.genfromtxt(csvfile, dtype=None).tolist()
imglist.sort()

if (os.path.isfile(input_zone_polygon)):
  vecDS = ogr.Open(input_zone_polygon)
else:
  print("File: %s does not exist....returning" % (input_zone_polygon))
  sys.exit(0)

lyr = vecDS.GetLayer()
sourceSR = lyr.GetSpatialRef()
feat = lyr.GetNextFeature()

geom = feat.GetGeometryRef()
if (geom.GetGeometryName() == 'MULTIPOLYGON'):
  count = 0
  pointsX = []; pointsY = []
  for polygon in geom:
    geomInner = geom.GetGeometryRef(count)
    ring = geomInner.GetGeometryRef(0)
    numpoints = ring.GetPointCount()
    for p in range(numpoints):
      lon, lat, z = ring.GetPoint(p)
      pointsX.append(lon)
      pointsY.append(lat)
    count += 1
elif (geom.GetGeometryName() == 'POLYGON'):
  ring = geom.GetGeometryRef(0)
  numpoints = ring.GetPointCount()
  pointsX = []; pointsY = []
  for p in range(numpoints):
    lon, lat, z = ring.GetPoint(p)
    pointsX.append(lon)
    pointsY.append(lat)
else:
  sys.exit("ERROR: Geometry needs to be either Polygon or Multipolygon")

testlon = pointsX[0]
testlat = pointsY[0]

utmzone = utm.from_latlon(testlat, testlon)[2]

targetSR = osr.SpatialReference()
targetSR.ImportFromEPSG(32600 + utmzone)
coordTrans = osr.CoordinateTransformation(sourceSR ,targetSR)

geom.Transform(coordTrans)

# Get extent of feature
geom = feat.GetGeometryRef()
if (geom.GetGeometryName() == 'MULTIPOLYGON'):
  count = 0
  pointsX = []; pointsY = []
  for polygon in geom:
    geomInner = geom.GetGeometryRef(count)
    ring = geomInner.GetGeometryRef(0)
    numpoints = ring.GetPointCount()
    for p in range(numpoints):
      lon, lat, z = ring.GetPoint(p)
      pointsX.append(lon)
      pointsY.append(lat)
    count += 1
elif (geom.GetGeometryName() == 'POLYGON'):
  ring = geom.GetGeometryRef(0)
  numpoints = ring.GetPointCount()
  pointsX = []; pointsY = []
  for p in range(numpoints):
    lon, lat, z = ring.GetPoint(p)
    pointsX.append(lon)
    pointsY.append(lat)
else:
  sys.exit("ERROR: Geometry needs to be either Polygon or Multipolygon")

xmin = min(pointsX) - (3.0 * 50)
xmax = max(pointsX) + (3.0 * 50)
ymin = min(pointsY) + ((-3.0) * 50)
ymax = max(pointsY) - ((-3.0) * 50)

print("Bounding Box: %12.2f %12.2f %12.2f %12.2f" % (xmin, xmax, ymin, ymax))
focal_bounds = (xmin, xmax, ymin, ymax)
print(pointsX)
print(pointsY)

rcx = []
rcy = []

## for j,Xval in enumerate(pointsX):
##   rcx.append(np.round((Xval - xmin)/3.))
##   rcy.append(np.round((ymax - pointsY[j])/3.))

## bounds = [[rcx[0], rcy[0]], [rcx[1], rcy[1]], [rcx[2], rcy[2]], [rcx[3], rcy[3]], [rcx[4], rcy[4]]]
## bounds = np.asarray(bounds)

bounds = [[pointsX[0], pointsY[0]], [pointsX[1], pointsY[1]], [pointsX[2], pointsY[2]], [pointsX[3], pointsY[3]], [pointsX[4], pointsY[4]]]

for i,infile in enumerate(imglist):
  if (os.path.isfile(os.path.join(rootDir,infile.decode("utf-8")))):
    # Open data
    rasterDS = gdal.Open(os.path.join(rootDir,infile.decode("utf-8")), gdal.GA_ReadOnly)
  else:
    print("File: %s does not exist....skipping" % (os.path.join(rootDir,infile.decode("utf-8"))))
    continue

  # Get raster georeference info
  gt = rasterDS.GetGeoTransform()
  xOrigin = gt[0]
  yOrigin = gt[3]
  pixelWidth = gt[1]
  pixelHeight = gt[5]
 
  img_bounds = (gt[0], gt[0]+(rasterDS.RasterXSize*gt[1]), gt[3]+(rasterDS.RasterYSize*gt[5]), gt[3])

  (focalinfo, imginfo) = get_overlap_info(focal_bounds, gt[1], img_bounds, gt[1])

  # Specify offset and rows and columns to read
  xoff = int((xmin - xOrigin)/pixelWidth)
  yoff = int((ymax - yOrigin)/pixelHeight)
  xcount = int((xmax - xmin)/pixelWidth)+1
  ycount = int((ymin - ymax)/pixelHeight)+1

  ## check to make sure we don't go out of bounds on image
  ## if (xoff < 0) or (yoff < 0) or ((xcount+xoff) > rasterDS.RasterXSize) or ((ycount+yoff) > rasterDS.RasterYSize):
  ##   print("Skipping %s out of bounds for this polygon"% (infile))
  ##   continue

  red = rasterDS.GetRasterBand(3)
  green = rasterDS.GetRasterBand(2)
  blue = rasterDS.GetRasterBand(1)
  ncols = rasterDS.RasterXSize
  nrows = rasterDS.RasterYSize

  reddata = red.ReadAsArray(imginfo[0], imginfo[1], imginfo[2], imginfo[3])
  greendata = green.ReadAsArray(imginfo[0], imginfo[1], imginfo[2], imginfo[3])
  bluedata = blue.ReadAsArray(imginfo[0], imginfo[1], imginfo[2], imginfo[3])

  reddatanew = np.zeros((ycount, xcount), dtype=np.int)
  reddatanew[focalinfo[1]:(focalinfo[1]+focalinfo[3]), focalinfo[0]:(focalinfo[0]+focalinfo[2])] = reddata
  redmin = np.min(reddata[np.greater(reddata, 0)])
  del reddata
  reddata = sp.bytescale(reddatanew, cmin=redmin)

  greendatanew = np.zeros((ycount, xcount), dtype=np.int)
  greendatanew[focalinfo[1]:(focalinfo[1]+focalinfo[3]), focalinfo[0]:(focalinfo[0]+focalinfo[2])] = greendata
  greenmin = np.min(greendata[np.greater(greendata, 0)])
  del greendata
  greendata = sp.bytescale(greendatanew, cmin=greenmin)

  bluedatanew = np.zeros((ycount, xcount), dtype=np.int)
  bluedatanew[focalinfo[1]:(focalinfo[1]+focalinfo[3]), focalinfo[0]:(focalinfo[0]+focalinfo[2])] = bluedata
  bluemin = np.min(bluedata[np.greater(bluedata, 0)])
  del bluedata
  bluedata = sp.bytescale(bluedatanew, cmin=bluemin)

  fig = plt.figure()
  timer = fig.canvas.new_timer(interval=6000)
  timer.add_callback(close_event)

  plt.title(os.path.basename(infile.decode("utf-8"))[0:23])
  plt.plot(pointsX, pointsY, 'r-', linewidth=2.0, zorder=1)
  plt.imshow(np.stack((reddata, greendata, bluedata), axis=2), zorder=0, extent=[xmin, xmax, ymin, ymax])

  timer.start()
  plt.show()

  targetDS, red, green, blue = None, None, None, None
  fig, timer = None, None

vecDS, lyr, geom = None, None, None
