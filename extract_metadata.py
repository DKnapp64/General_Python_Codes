#!/bin/env python3
import numpy as np
import gdal
import os, sys

def main(indir, outcsv):
  ## 20190723_204909_85_105d_3B_AnalyticMS_SR.tif
  inlist = glob.glob(indir+os.path.sep+"*3B_Analytic_SR.tif")

  inlist = sort(inlist)

  for thisimg in inlist:
    inDS = gdal.Open(thisimg, gdal.GA_ReadOnly)
    gt = inDS.GetGeoTransform()
    srs = osr.SpatilaReference()
    proj = gdal.GetProjection()
    srs.ImportFromWkt(proj)
    imgutmz = srs.GetUTMZone()
    aot = 
