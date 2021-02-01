#!/usr/bin/python
import gdal, ogr, osr
import numpy as np
import sys

# Open data
input_ds = gdal.Open(inputfile, gdal.GA_ReadOnly)

# Read raster as arrays
banddataraster = input_ds.GetRasterBand(1)

## Get the geotransform
gt = input_ds.GetGeoTransform()

## here, xoff and yoff are the offsets in X and Y from the upper left corner of the image.
xoff = 0
yoff = 0
xcount = input_ds.RasterXSize
ycount = input_ds.RasterYSize

## get data and hold it in a Numpy array
dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)

# Create for target raster the same projection as for the input raster
raster_srs = osr.SpatialReference()
raster_srs.ImportFromWkt(input_ds.GetProjectionRef())

target_ds = gdal.GetDriverByName('ENVI').Create('', input_ds.RasterXSize, input_ds.RasterYSize, 1, gdal.GDT_Float32)
target_ds.SetProjection(raster_srs.ExportToWkt())
target_ds.SetGeoTransform(gt)

outband = target_ds.GetRasterBand(1)
outband.WriteArray(dataraster)

## close the data sets
raster, target_ds = None, None
