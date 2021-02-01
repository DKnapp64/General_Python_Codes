#!/bin/env python3
import gdal, osr
import os, sys
import numpy as np
import math

def main(tile, ascdesc):
  indir = '/scratch/pbrodrick/bleaching_web_graphics/bottom_reprocess/'
  
  thedates = ['20190701_to_20190708', '20190708_to_20190715', 
  '20190715_to_20190722', '20190722_to_20190729', '20190729_to_20190805'
  '20190805_to_20190812', '20190812_to_20190819', '20190819_to_20190826',
  '20190826_to_20190902', '20190902_to_20190909', '20190909_to_20190916']
  
  
  outfile = '/scratch/dknapp4/Hawaii_Weekly/gather/' + tile + '_' + ascdesc+ '_numobs.tif'

  tempfile = indir + ascdesc + '_' + thedates[0] + os.path.sep + tile + '_br.tif'
  if os.path.exists(tempfile):
    tmpDS = gdal.Open(tempfile, gdal.GA_ReadOnly)
  else:
    print("File %s does not exist " % (tempfile)) 
    sys.exit(0)

  gt = tmpDS.GetGeoTransform()
  dims = [tmpDS.RasterXSize, tmpDS.RasterYSize]

  out = np.zeros((dims[1], dims[0]), dtype=np.uint8)
  drv = gdal.GetDriverByName('GTiff')
  outDS = drv.Create(outfile, dims[0], dims[1], 1, gdal.GDT_Byte)
  outDS.SetGeoTransform(gt)
  theproj = osr.SpatialReference()                                            
  theproj.ImportFromWkt(tmpDS.GetProjectionRef())                             
  outDS.SetProjection(theproj.ExportToWkt())  
  tmpDS = None

  for j in thedates:
    infile = indir + ascdesc + '_' + j + os.path.sep + tile + '_br.tif'
    if os.path.exists(infile):
      inDS = gdal.Open(infile, gdal.GA_ReadOnly)
    else:
      print("File %s does not exist " % (tempfile)) 
      continue
    ingt = inDS.GetGeoTransform()
    indims = [inDS.RasterXSize, inDS.RasterYSize]
    if (indims[0] != dims[0]) or (indims[1] != dims[1]):
      print("Dimensions are not equal ")
      sys.exit(0)
    if (gt[0] != ingt[0]) or (gt[3] != ingt[3]):
      print("Upper left corner is not equal ")
      sys.exit(0)
    data = inDS.GetRasterBand(1).ReadAsArray() 
    yindex, xindex = np.indices(data.shape)
    good = np.greater(data, 0)
    out[good] += 1
    inDS = None
  outDS.GetRasterBand(1).WriteArray(out)
  outDS.FlushCache()

  outDS = None 

  ## ul = [-17845905.865,2543824.301]
  ## dims = [131072, 86016]
  ## res = [4.777314267160171,-4.777314267160171]
  
if __name__ == "__main__":                                                      
                                                                                
  if len( sys.argv ) != 3:
    print("[ ERROR ] you must supply 2 arguments: gather_view_stats_single.py tile ascdesc")
    sys.exit( 0 )                                                               
                                                                                
  main( sys.argv[1], sys.argv[2] )
