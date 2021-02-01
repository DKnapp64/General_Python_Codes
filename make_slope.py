#!/bin/env python
import gdal
import numpy as np
import os, sys
import math

def slope(win3x3, res):
  dzdx = ((win3x3[0,2] + (2.0 * win3x3[1,2]) + win3x3[2,2]) \
    - (win3x3[0,0] + (2.0 * win3x3[1,0]) + win3x3[2,0])) / (8.0 * res)
  dzdy = ((win3x3[2,0] + (2.0 * win3x3[2,1]) + win3x3[2,2]) \
    - (win3x3[0,0] + (2.0 * win3x3[0,1]) + win3x3[0,2])) / (8.0 * res)

  slopeval = math.atan(math.sqrt(dzdx**2 + dzdy**2)) * 57.29578
  return (slopeval)


def main(infile):

  if os.path.exists(infile):
    inDS = gdal.Open(infile, gdal.GA_ReadOnly)
  else:
    print('File %s does not exist, quitting.' % (infile))

  gt = inDS.GetGeoTransform()
  proj = inDS.GetProjection()

  xsize = inDS.RasterXSize
  ysize = inDS.RasterYSize

  drv = gdal.GetDriverByName('GTiff')

  print(os.path.splitext(infile)[0]+'_slope.tif')

  outDS = drv.Create(os.path.splitext(infile)[0]+'_slope.tif', xsize, ysize, 1, 
    eType=inDS.GetRasterBand(1).DataType)
  outDS.SetGeoTransform(gt)
  outDS.SetProjection(proj)
  outBand = outDS.GetRasterBand(1)
  outBand.WriteArray((np.zeros(xsize, dtype=np.float32) - 9999.).reshape((1,xsize)), 0, 0)

  win3 = np.zeros((3, xsize), dtype=np.float32)
  inBand = inDS.GetRasterBand(1)
  temp = inBand.ReadAsArray(0, 0, xsize, 3)
  win3 = np.copy(temp)
 
  for j in range(1, ysize-2): 
    outdat = np.zeros(xsize, dtype=np.float32) - 9999.
    for i in range(1, xsize-1):
      dat = win3[:, (i-1):(i+2)]
      if (np.sum(np.logical_or(np.less_equal(dat, 0), np.greater(dat, 6768))) > 0):
        outdat[i] = -9999.
        continue
      else:
        slp = slope(dat, gt[1])
        outdat[i] = slp
    outBand.WriteArray(outdat.reshape((1,xsize)), 0, j)
    win3 = np.roll(win3, -1, axis=0)
    newline = inBand.ReadAsArray(0, j+2, xsize, 1)
    win3[2,:] = newline[0,:]
    if ((j % 1000) == 0):
      print('Finished line %d of %d' % (j+1, ysize))

  outBand.SetNoDataValue(-9999.)
  outBand.FlushCache()
  outDS.FlushCache()
  outDS, outBand, inDS, inBand = None, None, None, None


if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print('Please give an input file name')
    sys.exit( 0 )
  main( sys.argv[1] )
