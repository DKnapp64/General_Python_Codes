#!/bin/env python3
import gdal
import ogr
import os, sys
import glob

infiles = glob.glob('/scratch/dknapp4/tabi/tabi/Mosaics/*.pix')

for k,infile in enumerate(infiles):
  inDS = gdal.Open(infile, gdal.GA_ReadOnly)
  gt = inDS.GetGeoTransform()
  proj = inDS.GetProjection()
  indata = inDS.GetRasterBand(1).ReadAsArray()
  pixon = np.greater(indata, 0)

