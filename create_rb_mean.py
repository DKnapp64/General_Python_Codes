#!/bin/env python3
import gdal
import os, sys
import glob
import numpy as np
import warnings

def main(tileid):

  ## tileid = 'ascending/L15-0136E-1139N'
  fileList = glob.glob('2???????_to_2???????/'+tileid+'*_br_comp.tif')
  
  fileList = sorted(fileList)
  index = [k for k,obj in enumerate(fileList) if obj[0:8]=='20200420'][0]
  fileList = fileList[0:(index+1)]
  
  listDS = []
  dateList = []
  
  for k in fileList:
    listDS.append(gdal.Open(k, gdal.GA_ReadOnly))
    dateList.append(k[0:8])
  
  numdates = len(dateList)
  outmean = 'Means/' + os.path.basename(tileid) + '_br_mean.tif'
  drv = gdal.GetDriverByName('GTiff')
  outDS = drv.Create(outmean, 4096, 4096, 2, eType=gdal.GDT_Float32, options=['COMPRESS=LZW','TILED=YES'])
  outDS.SetGeoTransform(listDS[0].GetGeoTransform())
  outDS.SetProjection(listDS[0].GetProjection())
  outDS.GetRasterBand(1).SetNoDataValue(-9999.0)
  outDS.GetRasterBand(2).SetNoDataValue(-9999.0)
  
  for i in range(4):
    for j in range(4):
      patches = []
      for k in listDS:
        tempdata = k.GetRasterBand(1).ReadAsArray(j*1024, i*1024, 1024, 1024).astype(np.float)
        bad = np.less(tempdata, 0)
        tempdata[bad] = np.nan
        patches.append(tempdata)
  
      tempStack = np.stack(tuple(patches), axis=-1)
      del patches
      with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        meanData = np.nanmean(tempStack, axis=2)
        stdData = np.nanstd(tempStack, axis=2)
      badout1 = np.isnan(meanData)
      badout2 = np.isnan(stdData)
      meanData[badout1] = -9999.0
      stdData[badout2] = -9999.0
      outDS.GetRasterBand(1).WriteArray(meanData, xoff=j*1024, yoff=i*1024)
      outDS.GetRasterBand(2).WriteArray(stdData, xoff=j*1024, yoff=i*1024)
  
  for thisDS in listDS:
    thisDS = None
  
  outDS = None


if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print("[ USAGE ] you must supply 1 argument: create_rb_mean.py tileid")
    print(" where:   tileid is like ascending/L15-0136-1139N")
    sys.exit( 0 )

  main( sys.argv[1] )

