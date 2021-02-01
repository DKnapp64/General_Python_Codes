#!/bin/env python3
import gdal
import os, sys
import osr
import numpy as np
import subprocess
import time

def main(infile, thresh, outfile):
  inDS = gdal.Open(infile, gdal.GA_ReadOnly)
  theband = inDS.GetRasterBand(1).ReadAsArray()
  gt = inDS.GetGeoTransform()
  ## srs = osr.SpatialReference()
  proj = inDS.GetProjectionRef()
  ## srs.ImportFromWkt(proj)

  pixon = np.greater(theband, thresh)
 
  thedir = os.path.dirname(os.path.abspath(infile)) + os.path.sep
  temp1file = thedir + os.path.splitext(infile)[0]+"_temp1.tif"
  temp2file = thedir + os.path.splitext(infile)[0]+"_temp2.tif"
  outfile = thedir + outfile

  drv = gdal.GetDriverByName('GTiff')
  tmp1DS = drv.Create(temp1file, xsize=inDS.RasterXSize, ysize=inDS.RasterYSize, bands=3, eType=gdal.GDT_Byte, options=['COMPRESS=LZW','TILED=YES'])
  tmp1DS.SetGeoTransform(gt)
  tmp1DS.SetProjection(proj)
  outarr = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.uint8)
  blank = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.uint8)
  inDS = None
  outarr[pixon] = 255
  blank[pixon] = 1
  blank[pixon] = 1
  tmp1DS.GetRasterBand(1).WriteArray(outarr)
  tmp1DS.GetRasterBand(2).WriteArray(blank)
  tmp1DS.GetRasterBand(3).WriteArray(blank)
  tmp1DS.FlushCache()
  tmp1DS = None
  time.sleep(5)
  cmd1 = ['gdalwarp','-of','GTiff','-t_srs','EPSG:4326','-tr','0.000054345281862', '0.000054345281862','-srcnodata','0','-dstnodata','0','-co','TILED=YES',temp1file,temp2file]
  print(" ".join(cmd1))
  completed1 = subprocess.run(cmd1, check=True)
  print("Return Code: %d" % (completed1.returncode))
  cmd2 = ['gdal_translate', '-of', 'KMLSUPEROVERLAY', temp2file, outfile, '-co', 'FORMAT=PNG']
  print(" ".join(cmd2))
  completed2 = subprocess.run(cmd2, check=True)
  print("Return Code: %d" % (completed2.returncode))

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ USAGE ] you must supply 3 arguments: make_superoverlay.py infile threshold outfile")
    print("     infile: the input absolute difference file")
    print("     threshold: the threshold above which a pixel is turned 'ON' (turned Red) in output KMZ SuperOverlay")
    print("     outfile: the output KML SuperOverlay filename")
    print("")
    sys.exit( 0 )

  main( sys.argv[1], int(sys.argv[2]), sys.argv[3] )

