#!/bin/env python3
import numpy as np
import gdal
import os, sys
## from skimage.morphology import binary_erosion

def main(infile):
  ## infile = 'anomask_L15-0126E-1148N.tif'
  outfile = os.path.splitext(infile)[0] + '_full.tif'
  
  inDS = gdal.Open(infile, gdal.GA_ReadOnly)
  gt = inDS.GetGeoTransform()
  proj = inDS.GetProjection()
  imgcnt = inDS.RasterCount
  drv = gdal.GetDriverByName('GTiff')
  outDS = drv.Create(outfile, inDS.RasterXSize*16, inDS.RasterYSize*16, inDS.RasterCount, inDS.GetRasterBand(1).DataType)
  newgt = (gt[0], gt[1]/16., gt[2], gt[3], gt[4], gt[5]/16.)
  outDS.SetGeoTransform(newgt)
  outDS.SetProjection(proj)
  
  for i in range(imgcnt):
    imgcoarse = inDS.GetRasterBand(i+1).ReadAsArray()
    replic = np.repeat(np.repeat(imgcoarse, 16, axis=0), 16, axis=1) 
    outDS.GetRasterBand(i+1).WriteArray(replic)
  
  outDS.FlushCache()
  
  inDS, outDS = None, None
  
    
if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print("[ ERROR ] you must supply 1 arguments: make_outlines.py infile")
    sys.exit( 0 )

  main( sys.argv[1] )
  
