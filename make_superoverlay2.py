#!/bin/env python3
import gdal
import os, sys
import osr
import numpy as np
import subprocess
import time

def main(infile, minthresh, maxthresh, outfile):
  inDS = gdal.Open(infile, gdal.GA_ReadOnly)
  theband = inDS.GetRasterBand(1).ReadAsArray()
  gt = inDS.GetGeoTransform()
  ## srs = osr.SpatialReference()
  proj = inDS.GetProjectionRef()
  ## srs.ImportFromWkt(proj)

  pixon1 = np.greater(theband, maxthresh)
  pixon2 = np.logical_and(np.less(theband, maxthresh), np.greater(theband, (maxthresh+minthresh)/2.))
  pixon3 = np.logical_and(np.less(theband, (maxthresh+minthresh)/2.), np.greater(theband,minthresh))
 
  thedir = os.path.dirname(os.path.abspath(infile)) + os.path.sep
  temp1file = thedir + os.path.splitext(infile)[0]+"_temp1.tif"
  temp2file = thedir + os.path.splitext(infile)[0]+"_temp2.tif"
  outfile = thedir + outfile

  drv = gdal.GetDriverByName('GTiff')
  tmp1DS = drv.Create(temp1file, xsize=inDS.RasterXSize, ysize=inDS.RasterYSize, bands=3, eType=gdal.GDT_Byte, options=['COMPRESS=LZW','TILED=YES'])
  tmp1DS.SetGeoTransform(gt)
  tmp1DS.SetProjection(proj)
  red = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.uint8)
  green = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.uint8)
  blue = np.zeros((inDS.RasterYSize, inDS.RasterXSize), dtype=np.uint8)
  inDS = None
  ## make Red
  red[pixon1] = 255
  green[pixon1] = 1
  blue[pixon1] = 1
  ## make Green
  red[pixon2] = 1
  green[pixon2] = 255
  blue[pixon2] = 1
  ## make Yellow
  red[pixon3] = 255
  green[pixon3] = 255
  blue[pixon3] = 1
  tmp1DS.GetRasterBand(1).WriteArray(red)
  tmp1DS.GetRasterBand(2).WriteArray(green)
  tmp1DS.GetRasterBand(3).WriteArray(blue)
  tmp1DS.FlushCache()
  tmp1DS = None
  time.sleep(2)  ## just because I like give the file system time to catch up.
  cmd1 = ['gdalwarp','-of','GTiff','-t_srs','EPSG:4326','-tr','0.000054345281862', '0.000054345281862','-srcnodata','0','-dstnodata','0','-co','TILED=YES',temp1file,temp2file]
  print(" ".join(cmd1))
  completed1 = subprocess.run(cmd1, check=True)
  print("Return Code: %d" % (completed1.returncode))
  cmd2 = ['gdal_translate', '-of', 'KMLSUPEROVERLAY', temp2file, outfile, '-co', 'FORMAT=PNG']
  print(" ".join(cmd2))
  completed2 = subprocess.run(cmd2, check=True)
  print("Return Code: %d" % (completed2.returncode))

if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print("[ USAGE ] you must supply 4 arguments: make_superoverlay2.py infile minthresh maxthresh outfile")
    print("     infile: the input absolute difference file")
    print("     minthresh: the minimum threshold above which pixels will be colored yellow in KMZ SuperOverlay")
    print("     maxthresh: the maxmim threshold above which pixels will be coloted red in KMZ SuperOverlay")
    print("                Pixels that fall between min and max thresholds will be colored green in KMZ SuperOverlay")
    print("     outfile: the output KML SuperOverlay filename")
    print("")
    sys.exit( 0 )

  main( sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4] )

