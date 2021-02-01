#!/bin/env python3
import gdal, ogr, osr
import numpy as np
import sys, os
import warnings

def depth(inreflfile, chla, outdepthfile):

  warnings.filterwarnings("ignore")

  # if image file does not exist, skip it.
  if (os.path.isfile(inreflfile)):
    try:
      rasterDS = gdal.Open(inreflfile, gdal.GA_ReadOnly)
    except:
      print(("Error: Could not open file %s") % (inreflfile))
  else:
    print(("File %s does not exist") % (inreflfile))
    return

  ## turn command line value into a float
  chla = float(chla)

  try:
    greendata = rasterDS.GetRasterBand(2).ReadAsArray()
    nirdata = rasterDS.GetRasterBand(4).ReadAsArray()
  except:
    print(("Error: Could not read Green and/or NIR data from %s") % (inreflfile))
    

  ndwi = np.float32(greendata.astype(float) - nirdata)/np.float32(greendata.astype(float) + nirdata)
  good2 = np.logical_and(np.not_equal(nirdata, -9999), np.greater(ndwi, 0.0))

  (xind, yind) = np.indices((good2.shape[0], good2.shape[1]))
  xind = xind[good2]
  yind = yind[good2]

  bluedata = rasterDS.GetRasterBand(1).ReadAsArray()
  greendata = rasterDS.GetRasterBand(2).ReadAsArray()

  ## Use NIR band for glint removal
  bluedata = bluedata[good2] - nirdata[good2]
  greendata = greendata[good2] - nirdata[good2]

  ## calculate remote sensing reflectance
  rrsbigblue = bluedata/(np.pi * 10000.0)
  rrsbiggreen = greendata/(np.pi * 10000.0)

  ## calculate sub-surface reflectance
  rrsvecblue = rrsbigblue/(0.52 + (1.7 * rrsbigblue)) 
  rrsvecgreen = rrsbiggreen/(0.52 + (1.7 * rrsbiggreen)) 
  good3 = np.logical_and(np.greater(rrsvecgreen, 0.0), np.greater(rrsvecblue, 0.0))

  m0 = 52.083 * np.exp(0.957 * chla)
  m1 = 50.156 * np.exp(0.957 * chla)
  
  depthvec = m0 * (np.log(1000 * rrsvecblue[good3])/np.log(1000 * rrsvecgreen[good3])) - m1
  depthvecnew = np.ones(good3.shape[0], dtype=np.float32) * -9999.
  depthvecnew[good3] = depthvec
  toodeep = np.greater(depthvecnew, 15.0)
  depthvecnew[toodeep] = -9999.
  tooshallow = np.less(depthvecnew, 0.0)
  depthvecnew[tooshallow] = -9999.
  depthdata = np.ones((rasterDS.RasterYSize, rasterDS.RasterXSize), dtype=np.float32) * -9999.
  depthdata[good2] = depthvecnew
  
  drv = gdal.GetDriverByName('GTiff')
  outDS = drv.Create(outdepthfile, xsize=rasterDS.RasterXSize, ysize=rasterDS.RasterYSize, bands=1, eType=gdal.GDT_Float32)
  outDS.SetGeoTransform(rasterDS.GetGeoTransform())
  outDS.SetProjection(rasterDS.GetProjection())
  
  ## outDS.SetMetadataItem('data ignore value', "-9999.0", 'ENVI')

  outband = outDS.GetRasterBand(1)
  outband.SetNoDataValue(-9999)
  ## outband.SetDescription('Depth (m)')
  outband.WriteArray(depthdata)
  
  nirdata, bluedata, greendata, depthdata, rasterDS, outDS = None, None, None, None, None, None
