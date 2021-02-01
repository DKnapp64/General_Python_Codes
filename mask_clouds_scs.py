#!/bin/env python3
import gdal
import numpy as np
import os, sys
import glob
import subprocess
from skimage.transform import resize
from skimage.morphology import disk
from skimage.morphology import binary_erosion, binary_dilation
import warnings

"""This code is designed to do a rough masking of Planet normalized analytic mosaics that have unmasked clouds,
shadows, and other anomalies.  It depends on having a pre-computed Sentinel-2 cloud free mosaic, processed in 
Google Earth Engine.  It resamples the Planet imagery to 30m, like the Sentinel-2  data.  It does a comparison of
the Planet data to the Sentinel-2 to identify areas that are likely clouds or shadows.  It them resamples that
mask to the original Planet pixel size and runs morphology operators on them to dilate the mask to get
residual clouds and shadows.  The dilated mask is then applied to Planet data and written to an output
file that has "_masked" appended to the tile name. The resulting image can then be processed to bottom 
reflectance, just like the original surface reflectance images.

FOR SOUTH CHINA SEA ONLY!!
"""

def main(inimg):

  basedir = os.path.dirname(inimg)
  
  if not os.path.exists(inimg):
    print('File %s does not exist' % (inimg))
    sys.exit(0)
  if not os.path.exists(basedir):
    print('Directory %s does not exist' % (basedir))
    sys.exit(0)
  
  outimg = basedir + os.path.sep + os.path.splitext(os.path.basename(inimg))[0] + '_masked.tif'
  
  ## inimg = '../AscendingDescending/20200323_to_20200330/descending/L15-1866E-0911N.tif'
  inDS = gdal.Open(inimg, gdal.GA_ReadOnly)
  ingt = inDS.GetGeoTransform()
  inproj = inDS.GetProjection()
  xsize = inDS.RasterXSize
  ysize = inDS.RasterYSize
  ulx = ingt[0]
  uly = ingt[3]
  lrx = ingt[0] + (xsize * ingt[1])
  lry = ingt[3] + (ysize * ingt[5])
      
  clavgimg = '/data/gdcsdata/Research/Researcher/Knapp/SouthChinaSea/AscendingDescending/Sentinel2/southchinasea_sent2_mean.vrt'
  ## clavgimg = '/scratch/dknapp4/GBR/Clouds/landsat8_mean.vrt'
  claDS = gdal.Open(clavgimg, gdal.GA_ReadOnly)
  clagt = claDS.GetGeoTransform()
  xsizecla = claDS.RasterXSize
  ysizecla = claDS.RasterYSize
  clagt = claDS.GetGeoTransform()
  
  clstdimg = '/data/gdcsdata/Research/Researcher/Knapp/SouthChinaSea/AscendingDescending/Sentinel2/southchinasea_sent2_stdev.vrt'
  ## clstdimg = '/scratch/dknapp4/GBR/Clouds/landsat8_stdev.vrt'
  clsDS = gdal.Open(clavgimg, gdal.GA_ReadOnly)
  clsgt = clsDS.GetGeoTransform()
  xsizecls = clsDS.RasterXSize
  ysizecls = clsDS.RasterYSize
  clsgt = clsDS.GetGeoTransform()
  
  claDS, clsDS = None, None
  
  randit = str('%06d' % (np.random.randint(0,999999,1)[0]))
  l8avg ='temp_mean_'+randit+'.tif'
  l8std ='temp_stdev_'+randit+'.tif'
  
  for j in ['mean', 'stdev']:
    base = clavgimg[0:-8] + j + '.vrt'
    commdove1 = 'gdalwarp -of GTiff -r near -te '
    commdove2 = '%12.2f %12.2f %12.2f %12.2f -tr %6.2f %6.2f %s %s' % (ulx, lry, lrx, uly, clagt[1], clagt[1], base, 'temp_'+j+'_'+randit+'.tif') 
    myargs = (commdove1+commdove2).split()
    complete = subprocess.run(myargs, check=True)
  
  outfile = os.path.splitext(os.path.basename(inimg))[0] + '_' + randit + '_l8_sub.tif'
  commdove1 = 'gdalwarp -of GTiff -r average -te '
  commdove2 = '%12.2f %12.2f %12.2f %12.2f -tr %6.2f %6.2f %s %s' % (ulx, lry, lrx, uly, clagt[1], clagt[1], inimg, outfile) 
  myargs = (commdove1+commdove2).split()
  complete = subprocess.run(myargs, check=True)
  
  clearavgDS = gdal.Open(l8avg, gdal.GA_ReadOnly)
  clearavg1 = clearavgDS.GetRasterBand(1) 
  clearavg2 = clearavgDS.GetRasterBand(2) 
  clearavg3 = clearavgDS.GetRasterBand(3) 

  test = clearavg1.ReadAsArray()
  if (np.sum(np.isfinite(test)) < 200):
    print('%s not worth masking.  Few good points, could be problem with poor Landsat coverage' % (inimg))
    clearavgDS, clearstdDS = None, None
    os.remove(outfile)
    os.remove(l8avg)
    os.remove(l8std)
    sys.exit(0)
  
  clearstdDS = gdal.Open(l8std, gdal.GA_ReadOnly)
  clearstd1 = clearstdDS.GetRasterBand(1) 
  
  pDS = gdal.Open(outfile, gdal.GA_ReadOnly)
  planet1 = pDS.GetRasterBand(1)
  planet2 = pDS.GetRasterBand(2)
  planet3 = pDS.GetRasterBand(3)
  
  drv = gdal.GetDriverByName('GTiff')
  
  smmask = np.zeros((pDS.RasterYSize, pDS.RasterXSize), dtype=np.bool)
  
  for i in range(pDS.RasterYSize):
    line1 = planet1.ReadAsArray(0, i, pDS.RasterXSize, 1)
    line2 = planet2.ReadAsArray(0, i, pDS.RasterXSize, 1)
    line3 = planet3.ReadAsArray(0, i, pDS.RasterXSize, 1)
    plines  = np.stack((line1.squeeze(), line2.squeeze(), line3.squeeze()))
    pavg = np.mean(plines, axis=0)
    pgood = np.greater(np.sum(plines, axis=0), 0)
    
    clearline1 = clearavg1.ReadAsArray(0, i, clearavgDS.RasterXSize, 1)
    clearline2 = clearavg2.ReadAsArray(0, i, clearavgDS.RasterXSize, 1)
    clearline3 = clearavg3.ReadAsArray(0, i, clearavgDS.RasterXSize, 1)
    llines  = np.stack((clearline1.squeeze(), clearline2.squeeze(), clearline3.squeeze()))
    with warnings.catch_warnings():
      warnings.simplefilter("ignore")
      lavg = np.nanmean(llines, axis=0)

    lgood = np.logical_and(np.greater(np.sum(llines, axis=0), 0), np.all(np.isfinite(llines), axis=0))
  
    lstd = np.squeeze(clearstd1.ReadAsArray(0, i, clearavgDS.RasterXSize, 1))
  
    good = np.logical_and(pgood, lgood)
 
    sqdiff1 = np.power(plines[0,good] - llines[0,good], 2)
    sqdiff2 = np.power(plines[1,good] - llines[1,good], 2)
    sqdiff3 = np.power(plines[2,good] - llines[2,good], 2)
    
    dist = np.sqrt(sqdiff1 + sqdiff2 + sqdiff3)
    out = np.zeros(pDS.RasterXSize, dtype=np.float32)
    out[good] = dist
    ## notdark = np.less((lavg[good]-(lstd[good]*0.5)), pavg[good])
    distmask = np.less(out[good], 900.0)
    ## mask = np.logical_and(notdark, distmask)
    ## smmask[i, good] = mask.astype(np.uint8)
    smmask[i, good] = distmask.astype(np.uint8)
    
  opmask = np.logical_not(smmask)
  pDS, clearavgDS, clearstdDS = None, None, None
  
  os.remove(outfile)
  os.remove(l8avg)
  os.remove(l8std)
  
  ## if there are less than 200 good pixels in the image, do not mask.
  if (np.sum(smmask) < 200):
    print('%s not worth masking.  Few good points, could be problem with poor  Landsat coverage' % (inimg))
    sys.exit(0)
      
  ## Mask the Dove image
  
  ## inimg = '../AscendingDescending/20200323_to_20200330/descending/L15-1866E-0911N.tif'
  inDS = gdal.Open(inimg, gdal.GA_ReadOnly)
  ingt = inDS.GetGeoTransform()
  inproj = inDS.GetProjection()
  xsize = inDS.RasterXSize
  ysize = inDS.RasterYSize
  ulx = ingt[0]
  uly = ingt[3]
  
  ## bigmask = congrid(smmask, [4096, 4096], method='nearest', centre=True, minusone=True)
  bigmask = resize(smmask, (inDS.RasterYSize,inDS.RasterXSize))
  bigmask = bigmask.astype(np.bool)
  mydisk = disk(3, dtype=np.bool)
  berode = binary_erosion(bigmask, mydisk).astype(np.uint8)
  ## berode = bigmask
  
  mDS = drv.Create(outimg, inDS.RasterXSize, inDS.RasterYSize, inDS.RasterCount, 
    eType=inDS.GetRasterBand(1).DataType, options=['COMPRESS=LZW'])
  mDS.SetGeoTransform(ingt)
  mDS.SetProjection(inproj)
  
  for b in range(inDS.RasterCount):
    data = inDS.GetRasterBand(b+1).ReadAsArray()
    mask = np.equal(berode,0).astype(np.bool)
    data[mask] = 0
    mDS.GetRasterBand(b+1).WriteArray(data)
  
  inDS, mDS = None, None

if __name__ == "__main__":                                                      
                                                                                
  if len( sys.argv ) != 2:
    print("[ ERROR ] you must supply 1 argument: mask_clouds_scs.py in_surface_refl_file")
    print("where:")
    print("    in_surface_refl_file = input surface reflectance file")
    print("FOR SOUTH CHINA SEA ONLY")
    sys.exit( 0 )   
  
  main(sys.argv[1])
