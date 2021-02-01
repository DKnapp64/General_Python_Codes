#!/bin/env python3
import numpy as np
import osr
import gdal
import scipy.misc as sp
from tempfile import mkdtemp
from skimage import color
import os, sys
import shutil
import warnings

def main(infile):

  warnings.filterwarnings("ignore")

  ## open up input surface reflectance file
  inDS = gdal.Open(infile, gdal.GA_ReadOnly)
  ## temp = inDS.ReadAsArray()

  ## transpose it to make it band sequential
  ## temp2 = np.transpose(temp, (1,2,0))
  ## temp = None
  ## temp = temp2[:,:,0:3]
  ## temp2 = None

  ## make mask of data area
  maskdata = inDS.GetRasterBand(5).ReadAsArray() 
  mask = np.equal(maskdata, 65535)
  maskdata = None

  ## create NDWI data
  nir = inDS.GetRasterBand(4).ReadAsArray()
  tempgreen = inDS.GetRasterBand(2).ReadAsArray()
  ndwi = np.true_divide((tempgreen.astype(float) - nir), (tempgreen.astype(float) + nir))
  nir, tempgreen = None, None

  ## create temporary directory and filename to hold HSV image in a memory map
  tempdir = mkdtemp()
  filename1 = os.path.join(tempdir, 'tempfile1.dat')
  fp1 = np.memmap(filename1, dtype='float32', mode='w+', shape=(inDS.RasterYSize, inDS.RasterXSize, 4))

  ## load refl data into memory map
  for i in np.arange(4):
    tempband = inDS.GetRasterBand(int(i)+1).ReadAsArray()
    fp1[:,:,i] = tempband

  fp1.flush()

  ## identify good and bad pixels and make row and column indices for good data
  good2 = np.greater(ndwi, 0.0)  ## is water
  good = np.logical_and(mask, good2)
  print("Good values: %d" % (good.sum()))

  mask, good2 = None, None
  bad = np.logical_not(good)
  rows,cols = np.indices(good.shape)
  grows = rows[good]
  gcols = cols[good]
  
  ## get the 0.5 and 99.5 percentiles
  redmin = np.percentile(fp1[grows, gcols, 2], 0.5)
  greenmin = np.percentile(fp1[grows, gcols, 1], 0.5)
  bluemin = np.percentile(fp1[grows, gcols, 0], 0.5)
  redmax = np.percentile(fp1[grows, gcols, 2], 99.5)
  greenmax = np.percentile(fp1[grows, gcols, 1], 99.5)
  bluemax = np.percentile(fp1[grows, gcols, 0], 99.5)
  
  ## scale the data and clip it to the range 0.0-1.0
  red = (fp1[:,:,2]-redmin)/(redmax-redmin)
  green = (fp1[:,:,1]-greenmin)/(greenmax-greenmin)
  blue = (fp1[:,:,0]-bluemin)/(bluemax-bluemin)
  red = np.clip(red, 0.0, 1.0)
  green = np.clip(green, 0.0, 1.0)
  blue = np.clip(blue, 0.0, 1.0)

  ## hold the scaled data into a temporary array
  tempdata = np.zeros((fp1.shape[0], fp1.shape[1], 3), dtype=np.float32)
  tempdata[:,:,0] = red
  tempdata[:,:,1] = green
  tempdata[:,:,2] = blue
  temp, red, green, blue = None, None, None, None

  ## remove temporary directory and file
  shutil.rmtree(tempdir)

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
    print("[ ERROR ] you must supply 1 argument: make_rgb2hsv_mos.py insurfacerefl")
    print("    insurfacerefl = input surface reflectance file.")
    print("")

    sys.exit( 1 )

  main(sys.argv[1])

