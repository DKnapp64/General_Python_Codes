#!/bin/env python3
import gdal
import os, sys
import numpy as np
import glob
import warnings

def main(ascdesc, tile, stopat):
  
  ## blweeks = ['20190429_to_20190506', '20190506_to_20190513', 
  ##            '20190513_to_20190520', '20190520_to_20190527', 
  ##            '20190527_to_20190603', '20190603_to_20190610', 
  ##            '20190610_to_20190617', '20190617_to_20190624', 
  ##            '20190624_to_20190701', '20190701_to_20190708', 
  ##            '20190708_to_20190715', '20190715_to_20190722', 
  ##            '20190722_to_20190729']
  
  ## Bleaching weeks
  blweeks = ['20190401_to_20190408', 
  '20190408_to_20190415', '20190415_to_20190422', 
  '20190422_to_20190429',
  '20190429_to_20190506', '20190506_to_20190513',
  '20190513_to_20190520', '20190520_to_20190527',
  '20190527_to_20190603', '20190603_to_20190610',
  '20190610_to_20190617', '20190617_to_20190624',
  '20190624_to_20190701', '20190701_to_20190708',
  '20190708_to_20190715', '20190715_to_20190722',
  '20190722_to_20190729', '20190729_to_20190805',
  '20190805_to_20190812', '20190812_to_20190819',
  '20190819_to_20190826', '20190826_to_20190902',
  '20190902_to_20190909', '20190909_to_20190916',
  '20190916_to_20190923', '20190923_to_20190930',
  '20190930_to_20191007']

  g = 0

  while g < len(blweeks):
    g += 1
    if (blweeks[g-1][-8:] == stopat):
      break

  blweeks = blweeks[0:g]   
  drv = gdal.GetDriverByName('GTiff')
  
  dslist = []

  ## baseimg = np.zeros((4096,4096,5)) - 9999
  ## open the data sets for this group
  for k,theweek in enumerate(blweeks):
    rbtile = ascdesc + '_' + theweek + '/' + tile + '_br_comp.tif'
    if os.path.exists(rbtile):
      dslist.append(gdal.Open(rbtile, gdal.GA_ReadOnly))

  if (len(dslist) == 0):
    print('No images matching %s_*/%s_br_comp.tif up to %s' % (ascdesc, tile, theweek)
    sys.exit(0)

  gt = dslist[0].GetGeoTransform()
  proj = dslist[0].GetProjection()
  outtile = 'BleachFiles/'+ascdesc + '_' + tile + '_bleach_'+stopat+'.tif'
  outDS = drv.Create(outtile, 4096, 4096, 5, gdal.GDT_Float32)
  outDS.SetGeoTransform(gt)
  outDS.SetProjection(proj)
  Band1 = outDS.GetRasterBand(1)
  Band2 = outDS.GetRasterBand(2)
  Band3 = outDS.GetRasterBand(3)
  Band4 = outDS.GetRasterBand(4)
  Band5 = outDS.GetRasterBand(5)

  layerstack = []
  for w,thisDS in enumerate(dslist):
    layerstack.append(thisDS.GetRasterBand(1))
    ## print('Date %d  Min: %f  Max:%f' % (w, np.min(temp), np.max(temp)))
  lines = np.zeros((len(dslist), dslist[0].RasterXSize))
  for j in range(dslist[0].RasterYSize):
    for w,thisBand in enumerate(layerstack):
      lines[w,:] = thisBand.ReadAsArray(0, j, dslist[w].RasterXSize, 1)
    
    ## stack = np.dstack(layerstack)
    bad = np.logical_or(np.logical_not(np.isfinite(lines)), np.less(lines, -9000))
    lines[bad] = np.nan
    # I expect to see RuntimeWarnings in this block
    # There very well may be empty slices here (i.e., all Nans).  Suppress those warnings.
    with warnings.catch_warnings():
      warnings.simplefilter("ignore", category=RuntimeWarning)
      ## print('STACK: Date: %d, Min: %f  Max:%f' % (w, np.nanmin(temp), np.nanmax(temp)))
      meanval = np.expand_dims(np.nanmean(lines, axis=0), axis=0) 
      sdev = np.expand_dims(np.nanstd(lines, axis=0), axis=0)
      minval = np.expand_dims(np.nanmin(lines, axis=0), axis=0) 
      maxval = np.expand_dims(np.nanmax(lines, axis=0), axis=0) 
      medval = np.expand_dims(np.nanmedian(lines, axis=0), axis=0) 
    findex = np.logical_not(np.isfinite(meanval))
    meanval[findex] = -9999.0
    sdev[findex] = -9999.0
    minval[findex] = -9999.0
    maxval[findex] = -9999.0
    medval[findex] = -9999.0
    Band1.WriteArray(meanval.astype(np.float32), xoff=0, yoff=j)
    Band2.WriteArray(sdev.astype(np.float32), xoff=0, yoff=j)
    Band3.WriteArray(minval.astype(np.float32), xoff=0, yoff=j)
    Band4.WriteArray(maxval.astype(np.float32), xoff=0, yoff=j)
    Band5.WriteArray(medval.astype(np.float32), xoff=0, yoff=j)
    Band1.FlushCache()
    Band2.FlushCache()
    Band3.FlushCache()
    Band4.FlushCache()
    Band5.FlushCache()

  Band1.SetNoDataValue(-9999)
  Band2.SetNoDataValue(-9999)
  Band3.SetNoDataValue(-9999)
  Band4.SetNoDataValue(-9999)
  Band5.SetNoDataValue(-9999)
  outDS = None

  for k in dslist:
    k = None

  
if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ ERROR ] you must supply 3 arguments: make_general_bleach_image.py ascdesc tile stopat")
    print("where:")
    print("    ascdesc = to indicate whether image is ascending or descending.")
    print("    tile = the tile ID.")
    print("    stopat = the Monday date to stop.  e.g., 20191223")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3] )
