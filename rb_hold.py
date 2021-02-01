import gdal, ogr, osr
import numpy as np
import pyproj
import sys, os
import utm
import csv
import math
import warnings

def rb(inreflfile, chla, depthfile, outfile):

  warnings.filterwarnings("ignore")

  convalfile = os.path.dirname(os.path.realpath(__file__))+os.sep+"constant_values.csv"

  if os.path.isfile(convalfile): 
    try:
      convals = np.genfromtxt(convalfile, delimiter=",", names=True)
    except:
      print(("Error: could not read %s with with numpy.genfromtxt") % (convalfile))
  else:
    print(("File: %s does not exist") % (convalfile))
    
  ## Band center wavelengths
  bandwv = [480, 540, 610]
  
  # if image file does not exist, skip it.
  if (os.path.isfile(inreflfile)):
    try:
      reflDS = gdal.Open(inreflfile, gdal.GA_ReadOnly)
    except:
      print(("Error: could not open file %s with GDAL API") % (inreflfile))
  else:
    print(("File: %s does not exist") % (inreflfile))
    return

  ## set up values as described by Ji-Wei
  aph440 = 0.06 * math.pow(chla, 0.65)
  acdom440 = 0.5 * aph440
  bbp555 = 0.6 * math.pow(chla, 0.62)
  bbpvec = np.zeros((301,2), dtype=np.float)
  aphvec = np.zeros((301,2), dtype=np.float)
  bbvec = np.zeros((301,2), dtype=np.float)
  atvec = np.zeros((301,2), dtype=np.float)
  rrsdeepvec = np.zeros((301,2), dtype=np.float)
  acdomvec = np.zeros((301,2), dtype=np.float)
  dcvec = np.zeros((301,2), dtype=np.float)

  for d in np.arange(301):
    bbpvec[d,0] = (400 + d)
    bbvec[d,0] = (400 + d)
    atvec[d,0] = (400 + d)
    aphvec[d,0] = (400 + d)
    rrsdeepvec[d,0] = (400 + d)
    acdomvec[d,0] = (400 + d)
    dcvec[d,0] = (400 + d)

    bbpvec[d,1] = (0.002 + 0.02 * (0.5 - 0.25 * math.log10(chla)) * (550./float(400+d))) * bbp555
    bbvec[d,1] = convals[d]['bbw'] + bbpvec[d,1]
    aphvec[d,1] = (convals[d]['a0'] + convals[d]['a1'] * math.log(aph440)) * aph440
    acdomvec[d,1] = acdom440 * np.exp(-0.015 * ((400+d)-440))
    atvec[d,1] = convals[d]['aw'] + aphvec[d,1] + acdomvec[d,1]
    rrsdeepvec[d,1] = (0.089 + 0.125 * (bbvec[d,1]/(atvec[d,1] + bbvec[d,1]))) * (bbvec[d,1]/(atvec[d,1] + bbvec[d,1]))
    dcvec[d,1] = 1.03 * math.pow(1.0 + 2.4 * (bbvec[d,1]/(atvec[d,1]+bbvec[d,1])), 0.5)
  
  ## Read depth data 
  if (os.path.isfile(depthfile)):
    try:
      depDS = gdal.Open(depthfile, gdal.GA_ReadOnly)
      depthdata = depDS.GetRasterBand(1).ReadAsArray()
    except:
      print(("Error: Could not read depthdata into array from file %s") % (depthfile))
      return
  else:
    print(("Error: file %s does not exist") % (depthfile))
    return
    
  del depDS

  ## Read mask band (band 5 in Planet mosaics)
  if (reflDS.RasterCount > 4):
    try:
      mask = reflDS.GetRasterBand(5).ReadAsArray()
      maskdata = np.equal(mask, 65535)
      mask = None
    except:
      print(("Error: Could not get mask data from %s") % (inreflfile))
      return
  else:
    try:
      mask = reflDS.GetRasterBand(1).ReadAsArray()
      maskdata = np.not_equal(mask, -9999)
      mask = None
    except:
      print(("Error: Could not get mask data from %s") % (inreflfile))
      return

  good2 = np.logical_and(maskdata, np.logical_and(np.less_equal(depthdata, 15.0), np.greater(depthdata, 0.0)))
  maskdata = None

  ## Create output GDAL Data set of Rb result
  drv = gdal.GetDriverByName('GTiff')
  try:
    outDS = drv.Create(outfile, xsize=good2.shape[1], ysize=good2.shape[0], bands=3, eType=gdal.GDT_Int16)
  except:
    print(("Error: Cannot create output file %s for bottom reflectance") % (outfile))
    
  try:
    outDS.SetGeoTransform(reflDS.GetGeoTransform())
    outDS.SetProjection(reflDS.GetProjection())
    ## outDS.SetMetadataItem('wavelength', "{ 475.0, 540.0, 625.0 }", 'ENVI')
    ## outDS.SetMetadataItem('wavelength units', "nanometers", 'ENVI')
    ## outDS.SetMetadataItem('data ignore value', "-9999.", 'ENVI')
  except:
    print(("Error: Cannot create GeoTransform and/or Projection or MetaData for file %s for bottom reflectance") % (outfile))
    
  depthvec = depthdata[good2]
  del depthdata

  ## Read NIR band for doing glint correction on the other bands
  try:
    nirdata = reflDS.GetRasterBand(4).ReadAsArray()
  except:
    print(("Error: Cannot read NIR band from file %s") % (inreflfile))

  for band in np.arange(3).astype(int):
    try:
      thisdata = reflDS.GetRasterBand(int(band)+1).ReadAsArray()
    except:
      print(("Error: Cannot read band %d from file %s") % (int(band)+1,inreflfile))
      return

    ## Use NIR band for glint removal
    gooddata = thisdata[good2].astype(int) - nirdata[good2].astype(int)
    rrsbig = gooddata/(np.pi * 10000.0)
    rrsvec = rrsbig/(0.52 + 1.7 * rrsbig) 
    rrscvec =  rrsdeepvec[bandwv[band]-400,1] * (1.0 - np.exp(-dcvec[bandwv[band]-400,1] \
      * (atvec[bandwv[band]-400,1] + bbvec[bandwv[band]-400,1]) * depthvec))

    rrsbvec = rrsvec - rrscvec
    dbvec = 1.05 * math.pow(1.0 + 5.5 * (bbvec[bandwv[band]-400,1]/(atvec[bandwv[band]-400,1] + bbvec[bandwv[band]-400,1])), 0.5)
    rbvec = (rrsbvec * np.pi)/(np.exp(-dbvec * (atvec[bandwv[band]-400,1] + bbvec[bandwv[band]-400,1]) * depthvec))
    rbout = np.ones((nirdata.shape[0], nirdata.shape[1]), dtype=np.int16) * -9999.
    rbout[good2] = rbvec * 10000
    outband = outDS.GetRasterBand(int(band)+1)
    
    outband.WriteArray(rbout.astype(np.int16))
    outband.SetNoDataValue(-9999)
    outband.FlushCache()

  del reflDS, outDS

