import numpy as np
import gdal, ogr, osr
from scipy.ndimage import label, filters
import sys

in_file = '/Volumes/DGE/Data/Shared/Labs/Asner/Private/Research/Researcher/Knapp/Temp/belize_coral_mosaic_iop_depth_filled'
outfile = 'belize_20170901_coral_head_segments'

########################################################
# Open data
## raster = gdal.Open(in_file)
ds = gdal.Open(in_file)

## get data type
datatype = ds.GetRasterBand(1).DataType

# Create for target raster the same projection as for the value raster
raster_srs = osr.SpatialReference()
raster_srs.ImportFromWkt(ds.GetProjectionRef())
## target_ds.SetProjection(raster_srs.ExportToWkt())

## Find the overlap between the two images
gt = ds.GetGeoTransform()
# r1 has left, top, right, bottom of datasets's bounds in geospatial coordinates.
r = [gt[0], gt[3], gt[0] + (gt[1] * ds.RasterXSize), gt[3] + (gt[5] * ds.RasterYSize)]

## intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]

# check to see if they intersect
## if ((intersection[2] < intersection[0]) or (intersection[1] < intersection[3])):
##   intersection = None

data = ds.GetRasterBand(1)
dataarray = data.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize)
headboolean = np.logical_and(np.greater(dataarray, 0.1), np.less(dataarray, 3.0))
headmask = np.zeros_like(headboolean, dtype=np.dtype('b'))
headmask[headboolean] = 1
denoised = filters.median_filter(headmask, 3)

coralheads, numcoralheads = label(headmask)

driver = ds.GetDriver()
outDs = driver.Create(outfile, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Int32, [ 'INTERLEAVE=BIL' ]) 
outDs.SetGeoTransform(gt)
outDs.SetProjection(raster_srs.ExportToWkt())

outBand = outDs.GetRasterBand(1)
outBand.WriteArray(coralheads)
outBand.FlushCache()
outBand.SetNoDataValue(0.0)

del data, outBand
del ds, outDs
