import numpy as np
import gdal
import scipy.misc as sp
from tempfile import mkdtemp
from skimage import color
import os, sys
import shutil
import warnings

def cleanup(tempdir):
  ## remove temporary directory and file
  shutil.rmtree(tempdir)


def myrgb2hsv(infile, outfile):

  warnings.filterwarnings("ignore")

  ## open up input surface reflectance file
  if os.path.isfile(infile):
    try:
      inDS = gdal.Open(infile, gdal.GA_ReadOnly)
    except:
      print(("Error: Could not open file %s:") % (infile))
      return
  else:
    print(("Error: File %s does not exist") % (infile))
    return
     
  ## make mask of data area
  if (inDS.RasterCount > 4):
    try:
      maskdata = inDS.GetRasterBand(5).ReadAsArray() 
      mask = np.equal(maskdata, 65535)
      maskdata = None
    except:
      print("Exception: problem creating mask")
      return
  if (inDS.RasterCount == 4):
    try:
      maskdata = inDS.GetRasterBand(1).ReadAsArray() 
      mask = np.not_equal(maskdata, -9999)
      maskdata = None
    except:
      print("Exception: problem creating mask")
      return
    
  ## create NDWI data
  try:
    nir = inDS.GetRasterBand(4).ReadAsArray()
    tempgreen = inDS.GetRasterBand(2).ReadAsArray()
  except:
    return
  ndwi = np.true_divide((tempgreen.astype(float) - nir), (tempgreen.astype(float) + nir))
  nir, tempgreen = None, None

  ## create temporary directory and filename to hold HSV image in a memory map
  tempdir = mkdtemp()
  filename1 = os.path.join(tempdir, 'tempfile1.dat')
  try:
    fp1 = np.memmap(filename1, dtype='float32', mode='w+', shape=(inDS.RasterYSize, inDS.RasterXSize, 4))
  except:
    print(("Error: Could not open temporary file %s") % (filename1))
    return

  ## load refl data into memory map
  for i in np.arange(4):
    try:
      tempband = inDS.GetRasterBand(int(i)+1).ReadAsArray()
      fp1[:,:,i] = tempband
    except:
      print(("Error: Could not load data into temporary file"))
      cleanup(tempdir)

  fp1.flush()

  ## identify good and bad pixels and make row and column indices for good data
  good2 = np.greater(ndwi, 0.0)  ## is water
  good = np.logical_and(mask, good2)
  if (good.sum() == 0):
    cleanup(tempdir)
    print(("No good pixels found for %s...skipping") % (infile))
    return
    
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
  cleanup(tempdir)
  tempdata[:,:,0] = red
  tempdata[:,:,1] = green
  tempdata[:,:,2] = blue
  temp, red, green, blue = None, None, None, None

  ## create HSV image from scaled RGB
  try:
    newcolor = color.rgb2hsv(tempdata)
  except:
    print(("Error: Could not process image %s to HSV") % (infile))  

  ## write out data
  envidrv = gdal.GetDriverByName('ENVI')

  try:
    outDS = envidrv.Create(outfile, inDS.RasterXSize, inDS.RasterYSize, 3, gdal.GDT_Float32)
  except:
    print(("Error: Problem creating output ENVI file %s") % (outfile))

  outDS.GetRasterBand(1).WriteArray(newcolor[:,:,0])
  outDS.GetRasterBand(2).WriteArray(newcolor[:,:,1])
  outDS.GetRasterBand(3).WriteArray(newcolor[:,:,2])
  outDS.SetGeoTransform(inDS.GetGeoTransform())
  outDS.SetProjection(inDS.GetProjection())
  outDS.FlushCache()
  outDS, inDS = None, None

