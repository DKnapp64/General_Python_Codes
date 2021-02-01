#!/bin/env python3
import numpy as np
import osr
import gdal
import scipy.misc as sp
from skimage import color
import os, sys

def main(infile):

  ## open up input surface reflectance file
  inDS = gdal.Open(infile, gdal.GA_ReadOnly)
  temp = inDS.ReadAsArray()
  ## transpose it to make it band sequential
  temp2 = np.transpose(temp, (1,2,0))
  temp = None
  temp = temp2[:,:,0:3]
  temp2 = None

  ## find the good pixels
  good = np.all(np.not_equal(temp, -9999), axis=2)
  rows, cols = np.indices(good.shape)
  grows = rows[good]
  gcols = cols[good]
  
  ## get the 0.5 and 99.5 percentiles
  redmin = np.percentile(temp[grows, gcols, 2], 0.5)
  greenmin = np.percentile(temp[grows, gcols, 1], 0.5)
  bluemin = np.percentile(temp[grows, gcols, 0], 0.5)
  redmax = np.percentile(temp[grows, gcols, 2], 99.5)
  greenmax = np.percentile(temp[grows, gcols, 1], 99.5)
  bluemax = np.percentile(temp[grows, gcols, 0], 99.5)
  
  ## scale the data and clip it to the range 0.0-1.0
  red = (temp[:,:,2]-redmin)/(redmax-redmin)
  green = (temp[:,:,1]-greenmin)/(greenmax-greenmin)
  blue = (temp[:,:,0]-bluemin)/(bluemax-bluemin)
  red = np.clip(red, 0.0, 1.0)
  green = np.clip(green, 0.0, 1.0)
  blue = np.clip(blue, 0.0, 1.0)

  ## hold the scaled data into a temporary array
  tempdata = np.zeros(temp.shape, dtype=np.float32)
  tempdata[:,:,0] = red
  tempdata[:,:,1] = green
  tempdata[:,:,2] = blue

  temp, red, green, blue = None, None, None, None

  ## create HSV image from scaled RGB
  newcolor = color.rgb2hsv(tempdata)

  ## write out data
  envidrv = gdal.GetDriverByName('ENVI')
  outfilename = os.path.splitext(os.path.basename(infile))[0]+'_hsv'
  outDS = envidrv.Create(outfilename, inDS.RasterXSize, inDS.RasterYSize, 3, gdal.GDT_Float32)
  outDS.GetRasterBand(1).WriteArray(newcolor[:,:,0])
  outDS.GetRasterBand(2).WriteArray(newcolor[:,:,1])
  outDS.GetRasterBand(3).WriteArray(newcolor[:,:,2])
  outDS.SetGeoTransform(inDS.GetGeoTransform())
  outDS.SetProjection(inDS.GetProjection())
  outDS.FlushCache()
  outDS, inDS = None, None


if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print("[ ERROR ] you must supply 1 argument: make_rgb2hsv.py insurfacerefl")
    print("    insurfacerefl = input surface reflectance file.")
    print("")

    sys.exit( 1 )

  main(sys.argv[1])

