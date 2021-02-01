#!/bin/env python3
import gdal, osr
import os, sys

def main(intile, inimg, outscript):

  f = open(outscript, 'w')

  baseDS = gdal.Open(intile, gdal.GA_ReadOnly)
  gt = baseDS.GetGeoTransform()
  resx = 4.777314267160000
  resy = -4.777314267160000
  xmin = gt[0]
  ymin = gt[3] + (resy * baseDS.RasterYSize)
  xmax = gt[0] + (resx * baseDS.RasterXSize)
  ymax = gt[3]


  outfile = os.path.splitext(os.path.basename(intile))[0] + "_pseudomerc.tif"

  f.write(("gdalwarp -t_srs EPSG:3857 -te %16lf %16lf %16lf %16lf -tr %16lf %16lf -tap -srcnodata 255 -dstnodata 255 -of GTiff %s %s\n") % (xmin, ymin, xmax, ymax, resx, resx, inimg, outfile))
  f.close()
  baseDS = None

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ ERROR ] you must supply 3 arguments: make_gdal_script.py intile inimg outscript")
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3] )
