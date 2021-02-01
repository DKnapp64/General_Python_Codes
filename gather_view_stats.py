#!/bin/env python3
import gdal
import os, sys
import numpy as np
import math
import pdb

indir = '/scratch/pbrodrick/bleaching_web_graphics/bottom_reprocess/mosaics/'

indescend = ['descending_20190701_to_20190708.tif', 
'descending_20190708_to_20190715.tif', 'descending_20190715_to_20190722.tif', 
'descending_20190722_to_20190729.tif', 'descending_20190729_to_20190805.tif', 
'descending_20190805_to_20190812.tif', 'descending_20190812_to_20190819.tif', 
'descending_20190819_to_20190826.tif', 'descending_20190826_to_20190902.tif', 
'descending_20190902_to_20190909.tif', 'descending_20190909_to_20190916.tif']

inascend = ['ascending_20190701_to_20190708.tif', 
'ascending_20190708_to_20190715.tif', 'ascending_20190715_to_20190722.tif', 
'ascending_20190722_to_20190729.tif', 'ascending_20190729_to_20190805.tif', 
'ascending_20190805_to_20190812.tif', 'ascending_20190812_to_20190819.tif', 
'ascending_20190819_to_20190826.tif', 'ascending_20190826_to_20190902.tif', 
'ascending_20190902_to_20190909.tif', 'ascending_20190909_to_20190916.tif']

ul = [-17845905.865,2543824.301]
dims = [131072, 86016]
res = [4.777314267160171,-4.777314267160171]

totaldec = np.zeros((dims[0], dims[1]), dtype=np.uint8)
## totalasc = np.zeros((dims[0], dims[1]), dtype=np.uint8)

numparts = math.floor(dims[0]/5000)
parts = np.zeros(numparts, dtype=np.int)
parts[:] = 5000
parts[-1] += (math.floor(dims[0] % 5000))

rollit = np.roll(parts, 1)
rollit[0] = 0

pstarts = np.zeros(numparts, dtype=np.int)
for temp in range(1,26):
  pstarts[temp] = np.sum(rollit[0:temp+1], dtype=np.int)

print("%16.3f, %16.3f" % (ul[0], ul[1]))

## parts = parts[0:1]
drv = gdal.GetDriverByName('GTiff')
outDS = drv.Create('descend_out.tif', dims[0], dims[1], 1, gdal.GDT_Byte)

for i,thispart in enumerate(parts):
  out = np.zeros((thispart, dims[1]), dtype=np.uint8)
  for j in indescend:
    inDS = gdal.Open(indir+j, gdal.GA_ReadOnly)
    gt = inDS.GetGeoTransform()
    xoffset = int(math.copysign(round(math.fabs((gt[0] - ul[0])/res[0])), (gt[0] - ul[0])/res[0]))
    yoffset = int(math.copysign(round((math.fabs((gt[3] - ul[1])/res[1]))), (gt[3] - ul[1])/res[1]))
    ext = np.asarray([xoffset, (pstarts[i]-yoffset)], dtype=np.int64)
    print("%s, %16.3f, %16.3f, %d, %d, %d, %d" % (j, gt[0], gt[3], 0, int(pstarts[i]-yoffset), int(inDS.RasterXSize-xoffset), int(parts[i]-yoffset)))
    data = inDS.GetRasterBand(1).ReadAsArray(0, int(pstarts[i]-yoffset), int(inDS.RasterXSize-xoffset), int(parts[i]-yoffset)) 
    yindex, xindex = np.indices(data.shape)
    good = np.greater(data, 0)
    yindex = yindex[good] + yoffset
    xindex = xindex[good] + xoffset
    out[yindex,xindex] += 1
    inDS = None
  outDS.GetRasterBand(1).WriteArray(out, xoff=xoffset, yoff=yoffset)

outDS = None
print("Finished Descending")

drv = gdal.GetDriverByName('GTiff')
outDS = drv.Create('ascend_out.tif', dims[0], dims[1], 1, gdal.GDT_Byte)

for i,thispart in enumerate(parts):
  out = np.zeros((thispart, dims[1]), dtype=np.uint8)
  for j in inascend:
    inDS = gdal.Open(indir+j, gdal.GA_ReadOnly)
    gt = inDS.GetGeoTransform()
    xoffset = int(math.copysign(round(math.fabs((gt[0] - ul[0])/res[0])), (gt[0] - ul[0])/res[0]))
    yoffset = int(math.copysign(round((math.fabs((gt[3] - ul[1])/res[1]))), (gt[3] - ul[1])/res[1]))
    ext = np.asarray([xoffset, (pstarts[i]-yoffset)], dtype=np.int64)
    print("%s, %16.3f, %16.3f, %d, %d, %d, %d" % (j, gt[0], gt[3], xoffset, yoffset, ext[0], ext[1]))
    data = inDS.GetRasterBand(1).ReadAsArray(int(ext[0]), int(ext[1]), int(inDS.RasterXSize-xoffset), int(parts[i]-yoffset)) 
    yindex, xindex = np.indices(data.shape)
    good = np.greater(data, 0)
    yindex = yindex[good] + yoffset
    xindex = xindex[good] + xoffset
    out[yindex,xindex] += 1
    outDS.GetRasterBand(1).WriteArray(out, xoff=xoffset, yoff=yoffset)
    inDS = None


outDS = None
print("Finished Ascending")
 
