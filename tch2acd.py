#!/bin/env python3
import gdal
import numpy as np
import os, sys

infile = 'peru_flightlines_tch'
outfile = 'peru_flightlines_acd.tif'

inDS = gdal.Open(infile, gdal.GA_ReadOnly)
tch = inDS.GetRasterBand(1).ReadAsArray()

bad = np.equal(tch, -9999)
acd = 0.8245 * np.power(tch, 1.573)
acd[bad] = -9999.0

drv = gdal.GetDriverByName('GTiff')
outDS = drv.Create(outfile, inDS.RasterXSize, inDS.RasterYSize, 1, eType=gdal.GDT_Float32, options=['COMPRESS=LZW'])
outDS.SetGeoTransform(inDS.GetGeoTransform())
outDS.SetProjection(inDS.GetProjection())
outDS.GetRasterBand(1).WriteArray(acd)
outDS.GetRasterBand(1).SetNoDataValue(-9999.)

inDS, outDS = None, None
