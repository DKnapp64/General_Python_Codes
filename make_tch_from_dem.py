#!/bin/env python2
import gdal, osr
import numpy as np
import sys, os

def main(infile, outfile):

  inDS = gdal.Open(infile, gdal.GA_ReadOnly)

  if (inDS.RasterCount == 2):
    surface = inDS.GetRasterBand(1).ReadAsArray()
    ground = inDS.GetRasterBand(2).ReadAsArray()

  minsurfval = np.nanmin(surface)
  maxsurfval = np.nanmax(surface)
  mingroundval = np.nanmin(ground)
  maxgroundval = np.nanmax(ground)

  print("Surface: %s, %f, %f" % (infile, minsurfval, maxsurfval))
  print("Ground: %s, %f, %f" % (infile, mingroundval, maxgroundval))

  gt = inDS.GetGeoTransform()
  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt(inDS.GetProjectionRef())

  good = np.logical_and(np.not_equal(surface, -9999.0), np.not_equal(ground, -9999.0))
  tch = np.ones_like(surface) * -9999.0

  tch[good] = surface[good] - ground[good]

  driver = gdal.GetDriverByName('ENVI')
  outDS = driver.Create(outfile, inDS.RasterXSize, inDS.RasterYSize, 1, gdal.GDT_Float32)
  outDS.SetGeoTransform(gt)
  outDS.SetProjection(raster_srs.ExportToWkt())

  outBand = outDS.GetRasterBand(1)
  outBand.WriteArray(tch)
  outBand.FlushCache()
  outBand.SetNoDataValue(-9999.0)

  del inDS, surface, ground, tch, outBand, outDS


if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print "[ ERROR ] you must supply two arguments: make_tch_from_dem.py indem outtch"
    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2] )

