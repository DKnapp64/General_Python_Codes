#!/bin/env python3
import gdal
import os, sys
import glob
import numpy as np

def main(tileid):

  inmean = 'Means/' + os.path.basename(tileid) + '_br_mean.tif'
  mDS = gdal.Open(inmean, gdal.GA_ReadOnly)
  meanData = mDS.GetRasterBand(1).ReadAsArray()
  gt = mDS.GetGeoTransform()
  proj = mDS.GetProjection()
  ## tileid = 'ascending/L15-0136E-1139N'

  fileList = glob.glob('2???????_to_2???????/'+tileid+'*_br_comp.tif')
  fileList = sorted(fileList)
  
  listDS = []
  dateList = []
  
  for k in fileList:
    listDS.append(gdal.Open(k, gdal.GA_ReadOnly))
    dateList.append(k[0:8])
  
  for j,week in enumerate(dateList):
    
    outweek = 'Means/' + week
    if not os.path.exists(outweek):
      os.mkdir(outweek)
    outname = outweek + '/' + tileid.split('/')[1] + '_diff.tif'
    drv = gdal.GetDriverByName('GTiff')
    outDS = drv.Create(outname, mDS.RasterXSize, mDS.RasterYSize, 1, 
      eType=gdal.GDT_Float32, options=['COMPRESS=LZW','TILED=YES'])
    outDS.SetGeoTransform(gt)
    outDS.SetProjection(proj)
    outDS.GetRasterBand(1).SetNoDataValue(-9999.0)
    
    inDS = gdal.Open(fileList[j], gdal.GA_ReadOnly)
    inData = inDS.GetRasterBand(1).ReadAsArray()
    good = np.logical_and(np.greater(inData, 0), np.greater(meanData, 0))
    diff = inData[good] - meanData[good]
    outarray = np.zeros((mDS.RasterYSize, mDS.RasterXSize), dtype=np.float) - 9999.0
    outarray[good] = diff
    outDS.GetRasterBand(1).WriteArray(outarray)
    inDS, outDS = None, None

  mDS = None
  
if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print("[ USAGE ] you must supply 1 argument: create_rb_diffs.py tileid")
    print(" where:   tileid is like ascending/L15-0136-1139N")
    sys.exit( 0 )

  main( sys.argv[1] )

