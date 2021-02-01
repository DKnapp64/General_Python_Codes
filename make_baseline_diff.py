#!/bin/env python3
import gdal
import numpy as np
import os, sys

infile = sys.argv[1]
## basefile = '/scratch/dknapp4/Hawaii_Weekly/AscendingDescending/baseline_rb.tif'
basefile = '/scratch/dknapp4/Hawaii_Weekly/AscendingDescending/rb_mosaic_20191125_to_20191202.tif'
outfile = os.path.splitext(infile)[0] + '_sentineldiff.tif'
## outfile = os.path.splitext(infile)[0] + '_basediff.tif'

inDS = gdal.Open(infile, gdal.GA_ReadOnly)
bDS = gdal.Open(basefile, gdal.GA_ReadOnly)

nxchunks = int(inDS.RasterXSize/4096)
nychunks = int(inDS.RasterYSize/4096)
print('Number of Chunks: %s %d %d' % (infile, nxchunks, nychunks))

if ((inDS.RasterXSize % 4096) > 0):
  print('File Xsize is not multiple of 4096')
  inDS = None
  sys.exit(0)

if ((inDS.RasterYSize % 4096) > 0):
  print('File Ysize is not multiple of 4096')
  inDS = None
  sys.exit(0)

igt = inDS.GetGeoTransform()
proj = inDS.GetProjection()
bgt = bDS.GetGeoTransform()

if not np.all((np.isclose(igt, bgt, atol=0.001))):
  print('File %s and basefile do not have the same Geotransform' % (infile))

iband = inDS.GetRasterBand(1)
bband = bDS.GetRasterBand(1)
drv = gdal.GetDriverByName('GTiff')
outDS = drv.Create(outfile, inDS.RasterXSize, inDS.RasterYSize, 1, gdal.GDT_Int16)
outDS.SetGeoTransform(igt)
outDS.SetProjection(proj)
oband = outDS.GetRasterBand(1)
oband.SetNoDataValue(-9999.0)

for i in range(nychunks):
  for j in range(nxchunks):
    idata = iband.ReadAsArray(j*4096, i*4096, 4096, 4096)
    bdata = bband.ReadAsArray(j*4096, i*4096, 4096, 4096)
    ## igood = np.logical_and(np.not_equal(idata, -9999), np.not_equal(idata, 0))
    ## bgood = np.logical_and(np.not_equal(bdata, -9999), np.not_equal(bdata, 0))
    ibad = np.logical_or(np.equal(idata, -9999), np.equal(idata, 0))
    bbad = np.logical_or(np.equal(idata, -9999), np.equal(idata, 0))
    diff = np.round(idata - bdata)
    diff[ibad] = -9999.0
    diff[bbad] = -9999.0
    oband.WriteArray(diff, xoff=j*4096, yoff=i*4096)
    ## print('Number of Chunks: %d %d %d %d' % (j+1, i+1, nxchunks, nychunks))
    

outDS.FlushCache()
inDS, bDS, outDS = None, None, None
   


