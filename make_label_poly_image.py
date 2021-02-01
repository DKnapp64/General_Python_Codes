import gdal
import os, sys
import numpy as np
from skimage.measure import label, regionprops
import glob


listfiles = glob.glob('coralsand/L15*_sand.tif')

drv = gdal.GetDriverByName('GTiff')

for thisfile in listfiles:
  outfile = 'coralsand/'+os.path.basename(thisfile)[0:15]+'_sandpolys.tif'
  inDS = gdal.Open(thisfile, gdal.GA_ReadOnly)
  inBand = inDS.GetRasterBand(1)
  gt = inDS.GetGeoTransform()
  proj = inDS.GetProjection()
  data = inBand.ReadAsArray()
  
  sand = np.zeros_like(data)
  sandindex = np.equal(data, 1)
  sand[sandindex] = 1
  
  outDS = drv.Create(outfile, inDS.RasterXSize, inDS.RasterYSize, 1, gdal.GDT_UInt32)
  outDS.SetGeoTransform(gt)
  outDS.SetProjection(proj)
  
  label_image = label(sand)
  
  outDS.GetRasterBand(1).WriteArray(label_image)
  outDS.FlushCache()
  inDS, inBand, outDS = None, None, None
  print(outfile)

