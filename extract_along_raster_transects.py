#!/bin/env python3
import gdal
import os, sys
import numpy as np

transfile = "/scratch/dknapp4/ASD/GPS/GPS_all_clean_spec_segments_edited_raster.tif"
datafile = "/scratch/dknapp4/Moorea_for_Nick/20190604_moorea_tile_sr_rb.tif"
outfile = "Moorea_avg_dove_rb_segments_20190712.csv"

transDS = gdal.Open(transfile, gdal.GA_ReadOnly)
transarr = transDS.GetRasterBand(1).ReadAsArray()
uniqvals = np.unique(transarr)

if (uniqvals[0] == 0):
  uniqvals = uniqvals[1:]

inDS = gdal.Open(datafile, gdal.GA_ReadOnly)
blue = inDS.GetRasterBand(1).ReadAsArray()
green = inDS.GetRasterBand(2).ReadAsArray()
red = inDS.GetRasterBand(3).ReadAsArray()
## nir = inDS.GetRasterBand(4).ReadAsArray()

transDS, inDS = None, None

if not(np.array_equal(blue.shape, transarr.shape)):
  print("Arrays are not the same size")
  sys.exit(1)

f = open(outfile, 'w')

for k in uniqvals:
  good = np.logical_and(np.equal(transarr, k), np.not_equal(blue,-9999.0))
  if (good.sum() > 0):
    meanblue = np.mean(blue[good])/10000.0
    meangreen = np.mean(green[good])/10000.0
    meanred = np.mean(red[good])/10000.0
    ## meannir = np.mean(nir[good])/10000.0
    sdevblue = np.std(blue[good])/10000.0
    sdevgreen = np.std(green[good])/10000.0
    sdevred = np.std(red[good])/10000.0
    ## sdevnir = np.std(nir[good])/10000.0
  ##   f.write(("%03d, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f\n") % (k, meanblue, meangreen, meanred, meannir, sdevblue, sdevgreen, sdevred, sdevnir))
    f.write(("%03d, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f\n") % (k, meanblue, meangreen, meanred, sdevblue, sdevgreen, sdevred))
  else:
  ##   f.write(("%03d, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f\n") % (k, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999))
    f.write(("%03d, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f\n") % (k, -9999, -9999, -9999, -9999, -9999, -9999))

f.close()


