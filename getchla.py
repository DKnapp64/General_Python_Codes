import numpy as np
import gdal
from tempfile import mkdtemp
import scipy.ndimage as s
from skimage.morphology import disk
from skimage.morphology import binary_erosion
from skimage.filters.rank import median
from skimage.measure import label
import shutil
import os, sys
import warnings

def getchla(inhsvfile, inreflfile):

  warnings.filterwarnings("ignore")

  if (os.path.isfile(inhsvfile)):
    try:
      hsvDS = gdal.Open(inhsvfile, gdal.GA_ReadOnly)
      reflDS = gdal.Open(inreflfile, gdal.GA_ReadOnly)
    except:
      print(("Error: Could not open file %s or %s") % (inhsvfile, inreflfile))
      return
  else:
    print(("HSV file does not exist for %s.  Must be an empty or minimally covered tile.") % (inreflfile)) 
    ## open text file as a placeholder with np.nan values
    with open(os.path.basename(inhsvfile)[0:-4]+'_info.txt', "w") as tfile:
      tfile.write(("%s, Chla: %10f, w: %10f, blue: %10f, green: %10f, red: %10f\n") % (os.path.basename(inreflfile), np.nan, np.nan, np.nan, np.nan, np.nan))
    return np.nan

  ## read reflectance data
  nir = reflDS.GetRasterBand(4).ReadAsArray()
  tempgreen = reflDS.GetRasterBand(2).ReadAsArray()
  ndwi = np.true_divide((tempgreen.astype(float) - nir), (tempgreen.astype(float) + nir))
  nir, tempgreen = None, None
  if (reflDS.RasterCount > 4):
    mask = reflDS.GetRasterBand(5).ReadAsArray()
    good1 = np.equal(mask, 65535)
    mask = None
  else:
    mask = reflDS.GetRasterBand(1).ReadAsArray()
    good1 = np.not_equal(mask, -9999)
    mask = None

  ## create temporary directory and filename to hold HSV image in a memory map
  tempdir = mkdtemp()
  filename1 = os.path.join(tempdir, 'tempfile1.dat') 
  fp1 = np.memmap(filename1, dtype='float32', mode='w+', shape=(hsvDS.RasterYSize, hsvDS.RasterXSize, hsvDS.RasterCount))
  
  ## load HSV data into memory map
  for i in np.arange(hsvDS.RasterCount):
    try:
      tempband = hsvDS.GetRasterBand(int(i)+1).ReadAsArray()
      fp1[:,:,i] = tempband
    except:
      print("Error reading in HSV data to temporary file")
      shutil.rmtree(tempdir)
      return np.nan

  fp1.flush()

  ## identify good and bad pixels and make row and column indices for good data
  good2 = np.greater(ndwi, 0.0)  ## is water
  good = np.logical_and(good1, good2)
  good1, good2 = None, None
  print("Good values: %d" % (good.sum()))

  if (good.sum() < 10):
    print(("Too few good pixels remaining to do Chl-a estimate for file %s.") % (inreflfile))

    shutil.rmtree(tempdir)
    if (os.path.isfile(inhsvfile)):
      os.remove(inhsvfile)
    if (os.path.isfile(inhsvfile+".hdr")):
      os.remove(inhsvfile+".hdr")

    ## open text file as a placeholder with np.nan values
    with open(os.path.basename(inhsvfile)[0:-4]+'_info.txt', "w") as tfile:
      tfile.write(("%s, Chla: %10f, w: %10f, blue: %10f, green: %10f, red: %10f\n") % (os.path.basename(inreflfile), np.nan, np.nan, np.nan, np.nan, np.nan))

    return np.nan
    
  rows,columns = np.indices(good.shape)
  goodrows = rows[good]
  goodcols = columns[good]
  
  ## find mode of hue distribution around the blue stuff
  ## make histogram of the Hue band
  histohue, edgeshue = np.histogram(fp1[goodrows, goodcols, 0], bins=255)

  ## determine the centers of the Hue bins based on the edges of the bins
  edgecenters = np.interp(np.arange(edgeshue.shape[0]-1)+0.5, np.arange(edgeshue.shape[0]), edgeshue) 

  ## find where hue is greater than 0.4 and less than 1.0
  ## this narrows the selection are to the blue area
  myedges = np.logical_and(np.greater(edgecenters, 0.4), np.less(edgecenters, 1.0))
  edgeshue2 = edgecenters[myedges]
  histohue2 = histohue[myedges]
  if ((edgeshue2.size == 0) or (histohue2.size == 0)):
    shutil.rmtree(tempdir)
    if (os.path.isfile(inhsvfile)):
      os.remove(inhsvfile)
    if (os.path.isfile(inhsvfile+".hdr")):
      os.remove(inhsvfile+".hdr")

    ## open text file as a placeholder with np.nan values
    with open(os.path.basename(inhsvfile)[0:-4]+'_info.txt', "w") as tfile:
      tfile.write(("%s, Chla: %10f, w: %10f, blue: %10f, green: %10f, red: %10f\n") % (os.path.basename(inreflfile), np.nan, np.nan, np.nan, np.nan, np.nan))

    return np.nan
    
  ## find the peak of the blue area and get an index of those pixels
  peakblue = np.argmax(histohue2)
  indexhue = np.logical_and(np.greater(fp1[:,:,0], 0.4), np.less(fp1[:,:,0], 1.0))
  rowhue = rows[indexhue]
  colhue = columns[indexhue]
  stdhue = np.std(fp1[rowhue,colhue,0])
  
  ## find the good saturation range
  ## make histogram of the Saturation band
  histosat, edgessat = np.histogram(fp1[goodrows, goodcols, 1], bins=255)

  ## determine the centers of the Hue bins based on the edges of the bins
  edgecenters = np.interp(np.arange(edgessat.shape[0]-1)+0.5, np.arange(edgessat.shape[0]), edgessat) 

  ## find where hue is greater than 0.4 and less than 1.0
  ## this narrows the selection are to the blue area
  myedges = np.logical_and(np.greater(edgecenters, 0.8), np.less(edgecenters, 1.01))
  edgessat2 = edgecenters[myedges]
  histosat2 = histosat[myedges]
  if ((edgessat2.size == 0) or (histosat2.size == 0)):
    shutil.rmtree(tempdir)
    if (os.path.isfile(inhsvfile)):
      os.remove(inhsvfile)
    if (os.path.isfile(inhsvfile+".hdr")):
      os.remove(inhsvfile+".hdr")

    ## open text file as a placeholder with np.nan values
    with open(os.path.basename(inhsvfile)[0:-4]+'_info.txt', "w") as tfile:
      tfile.write(("%s, Chla: %10f, w: %10f, blue: %10f, green: %10f, red: %10f\n") % (os.path.basename(inreflfile), np.nan, np.nan, np.nan, np.nan, np.nan))

    return np.nan
    
  ## find the peak of the blue area and get an index of those pixels
  peaksat = np.argmax(histosat2)
  indexsat = np.logical_and(np.greater(fp1[:,:,1], 0.8), np.less(fp1[:,:,1], 1.01))
  rowsat = rows[indexsat]
  colsat = columns[indexsat]
  stdsat = np.std(fp1[rowsat,colsat,0])

  ## similar to what we did with the Hue, look for the darkest pixels in the Value (Intensity) data
  histovalue, edgesvalue = np.histogram(fp1[goodrows, goodcols, 2], bins=255)
  edgecenters = np.interp(np.arange(edgesvalue.shape[0]-1)+0.5, np.arange(edgesvalue.shape[0]), edgesvalue) 

  ## find where value is less than 0.5 and greater than 0.2
  ## this narrows the selection are to the darkest areas
  myedges = np.logical_and(np.greater_equal(edgecenters, 0.2), np.less(edgecenters, 0.5))
  edgesvalue2 = edgecenters[myedges]
  histovalue2 = histovalue[myedges]
  peakdark = np.argmax(histovalue2)

  print(("Peak Dark: %6.1f") % (edgesvalue2[peakdark]))

  ## indexval = np.logical_and(np.greater_equal(fp1[:,:,2], 0.0), np.less(fp1[:,:,2], 0.1))
  indexval = np.logical_and(np.greater_equal(fp1[:,:,2], 0.25), np.less(fp1[:,:,2], 0.45))
  rowval = rows[indexval]
  colval = columns[indexval]
  stdval = np.std(fp1[rowval,colval,2])
  
  ## find those pixels that are the bluest and darkest pixels to use as an indicator of deep water
  goodhue = np.logical_and(np.greater(fp1[:,:,0], edgeshue2[peakblue]-stdhue), np.less(fp1[:,:,0], edgeshue2[peakblue]+stdhue))  
  goodvalue = np.logical_and(np.greater(fp1[:,:,2], edgesvalue2[peakdark]-2.5*stdval), np.less(fp1[:,:,2], edgesvalue2[peakdark]))  
  goodsat = np.logical_and(np.greater(fp1[:,:,1], edgessat2[peaksat]-stdsat), np.less(fp1[:,:,1], edgessat2[peaksat]+stdsat))  

  ## remove temporary directory and file
  shutil.rmtree(tempdir)

  ## use all of these conditions to find the pixels to used for getting deep water areas
  bluestuff = np.all(np.stack((goodhue, goodvalue, goodsat, good), axis=-1), axis=2)

  ## goodhue, goodvalue = None, None
  rowhue, colhue, rowval, colval, rowsat, colsat = None, None, None, None, None, None

  eroded = bluestuff

  ## print number of pixels after possible erosion
  print(("Number after erosion is %d") % (eroded.sum()))

  if (eroded.sum() == 0):
    print(("No good pixels remaining to do Chl-a estimate for file %s.") % (inreflfile))

    ## open text file as a placeholder with np.nan values
    with open(os.path.basename(inhsvfile)[0:-4]+'_info.txt', "w") as tfile:
      tfile.write(("%s, Chla: %10f, w: %10f, blue: %10f, green: %10f, red: %10f\n") % (os.path.basename(inreflfile), np.nan, np.nan, np.nan, np.nan, np.nan))

  ## read reflectance data and set to integer so that they are converted to SIGNED integers
  try:
    nir = reflDS.GetRasterBand(4).ReadAsArray().astype(int)
    tempred = reflDS.GetRasterBand(3).ReadAsArray().astype(int)
    tempgreen = reflDS.GetRasterBand(2).ReadAsArray().astype(int)
    tempblue = reflDS.GetRasterBand(1).ReadAsArray().astype(int)
  except:
    print(("Error: Problem with reading in surface Reflectance data for file %s.") % (inreflfile))

  ##  clip the NIR data to avoid negatives, setting them to 0.
  np.clip(nir, 0, None, out=nir)
  deepred = np.nanmean(tempred[eroded] - nir[eroded])/(np.pi * 10000)
  deepgreen = np.nanmean(tempgreen[eroded] - nir[eroded])/(np.pi * 10000)
  deepblue = np.nanmean(tempblue[eroded] - nir[eroded])/(np.pi * 10000)
  nir, tempred, tempgreen, tempblue = None, None, None, None

  ## calculate water column attenuation index 
  w = deepgreen - (0.46 * deepred) - (0.54 * deepblue)

  ## calculate Chl-a (Hu, Lee, and Franz 2012)
  chla = np.float_power(10, (-0.4909 + (191.659*w)))

  ## open text file and write out Chl-a value and other stats
  with open(os.path.basename(inhsvfile)[0:-4]+'_info.txt', "w") as tfile:
    tfile.write(("%s, Chla: %10f, w: %10f, blue: %10f, green: %10f, red: %10f\n") % (os.path.basename(inreflfile), chla, w, deepblue, deepgreen, deepred))

  ## write out mask of deep water area for diagnostic purposes
  envidrv = gdal.GetDriverByName('ENVI')
  outname = os.path.basename(inhsvfile)[0:-4]+'_bluemask'
  outDS = envidrv.Create(outname, reflDS.RasterXSize, reflDS.RasterYSize, 1, gdal.GDT_Byte)
  outDS.GetRasterBand(1).WriteArray(eroded.astype(np.uint8))
  outDS.SetGeoTransform(reflDS.GetGeoTransform())
  outDS.SetProjection(reflDS.GetProjection())
  outDS.FlushCache()
  outDS, fp1 = None, None

  return chla
