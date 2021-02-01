import numpy as np
import gdal, ogr, osr
from scipy.interpolate import interp1d
import sys

## in_file1 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/20170930A_EH021554_41_masked'
in_file1 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/20170930A_EH021554_182_masked'
##in_file2 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/outtesthisto'
## in_file2 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/20170930A_EH021554_42_masked'
in_file2 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch42_step1'
outfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch42_20170930_dimac'

########################################################
# Open data
## raster = gdal.Open(in_file)
ds1 = gdal.Open(in_file1)
ds2 = gdal.Open(in_file2)

## get data type
datatype = ds1.GetRasterBand(1).DataType

# Create for target raster the same projection as for the value raster
raster_srs = osr.SpatialReference()
raster_srs.ImportFromWkt(ds1.GetProjectionRef())
## target_ds.SetProjection(raster_srs.ExportToWkt())

## Find the overlap between the two images
gt1 = ds1.GetGeoTransform()
# r1 has left, top, right, bottom of datasets's bounds in geospatial coordinates.
r1 = [gt1[0], gt1[3], gt1[0] + (gt1[1] * ds1.RasterXSize), gt1[3] + (gt1[5] * ds1.RasterYSize)]

gt2 = ds2.GetGeoTransform()
# r2 has left, top, right, bottom of datasets's bounds in geospatial coordinates.
r2 = [gt2[0], gt2[3], gt2[0] + (gt2[1] * ds2.RasterXSize), gt2[3] + (gt2[5] * ds2.RasterYSize)]

intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]

# check to see if they intersect
if ((intersection[2] < intersection[0]) or (intersection[1] < intersection[3])):
  intersection = None

if intersection is not None:
  px1 = [int(np.round((intersection[0]-r1[0])/gt1[1])), \
         int(np.round((intersection[1]-r1[1])/gt1[5])), \
         int(np.round((intersection[2]-r1[0])/gt1[1])), \
         int(np.round((intersection[3]-r1[1])/gt1[5]))] 
  px2 = [int(np.round((intersection[0]-r2[0])/gt2[1])), \
         int(np.round((intersection[1]-r2[1])/gt2[5])), \
         int(np.round((intersection[2]-r2[0])/gt2[1])), \
         int(np.round((intersection[3]-r2[1])/gt2[5]))] 

driver = ds1.GetDriver()
outDs = driver.Create(outfile, ds1.RasterXSize, ds1.RasterYSize, ds1.RasterCount, datatype, [ 'INTERLEAVE=BIL' ]) 
outDs.SetGeoTransform(gt1)
outDs.SetProjection(raster_srs.ExportToWkt())

# Read raster as arrays
for band in range(ds1.RasterCount):
  data1 = ds1.GetRasterBand(band+1)
  dataarray1 = data1.ReadAsArray(px1[0], px1[1], px1[2]-px1[0], px1[3]-px1[1])
  data2 = ds2.GetRasterBand(band+1)
  dataarray2 = data2.ReadAsArray(px2[0], px2[1], px2[2]-px2[0], px2[3]-px2[1])

  # find good data
  good = np.logical_and(dataarray1 != 0.0, dataarray2 != 0.0)
  data1good = dataarray1[good].flatten()
  data2good = dataarray2[good].flatten()

  minval = np.min(np.append(data1good, data2good))
  maxval = np.max(np.append(data1good, data2good))
  data1hist = np.histogram(data1good, bins=50, range=(minval, maxval))
  data2hist = np.histogram(data2good, bins=50, range=(minval, maxval))

  binscombo = data1hist[1]

  nPixels = np.sum(good)

  cdf1 = []
  for k in range(0, len(data1hist[1])-1):
    b = np.sum(data1hist[0][:k]) 
    cdf1.append(float(b)/nPixels)

  cdf2 = []
  for j in range(0, len(data2hist[1])-1):
    g = np.sum(data2hist[0][:j]) 
    cdf2.append(float(g)/nPixels)

  ## im2 = np.interp(im1, cdf2, binscombo[:-1])
  ## new = np.zeros_like(dataarray1)
  ## new[good] = im2

  datafull1 = ds1.GetRasterBand(band+1)
  datafull1Band = datafull1.ReadAsArray(0, 0, ds1.RasterXSize, ds1.RasterYSize)
  datafull2 = ds2.GetRasterBand(band+1)
  datafull2Band = datafull2.ReadAsArray(0, 0, ds2.RasterXSize, ds2.RasterYSize)
  zero = np.equal(datafull1Band, 0.0)

  im1 = np.interp(datafull1Band, binscombo[:-1], cdf1)
  im2 = np.interp(im1, cdf2, binscombo[:-1])
  im2[zero] = 0.0

  outBand = outDs.GetRasterBand(band+1)
  outBand.WriteArray(im2)
  outBand.FlushCache()
  outBand.SetNoDataValue(0.0)

  del im2, im1, outBand

del outDs, ds1, ds2

