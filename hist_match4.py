import numpy as np
import gdal, ogr, osr
from scipy.interpolate import interp1d
import sys
## import pdb

listfiles = ['/Volumes/DGE/CAO/caodata/Scratch/dknapp/hybrid/20170905A_EH021554_190_bal_ort', \
             '/Volumes/DGE/CAO/caodata/Scratch/dknapp/hybrid/20170905A_EH021554_189_bal_ort']

## master image should always be last
master = 1

outfile = 'outtesthisto'

########################################################
# Open data
## raster = gdal.Open(in_file)
listdatasets = []

for file in listfiles:
  ds = gdal.Open(file)
  listdatasets.append(ds)

## get data type
datatype = listdatasets[0].GetRasterBand(1).DataType

# Create for target raster the same projection as for the value raster
raster_srs = osr.SpatialReference()
raster_srs.ImportFromWkt(listdatasets[0].GetProjectionRef())
## target_ds.SetProjection(raster_srs.ExportToWkt())

## Find the overlap between the images

## Get bounds of each image
listbounds = []

Xres = (listdatasets[0].GetGeoTransform())[1]
Yres = (listdatasets[0].GetGeoTransform())[5]

for ds in listdatasets:
  gt = ds.GetGeoTransform()
  # r has left, top, right, bottom of datasets's bounds in geospatial coordinates.
  r = [gt[0], gt[3], gt[0] + (gt[1] * ds.RasterXSize), gt[3] + (gt[5] * ds.RasterYSize)]
  listbounds.append(r)

minx = np.double(100000000.)
maxx = np.double(-100000000.)
miny = np.double(100000000.)
maxy = np.double(-100000000.)

for bnd in listbounds:
  if (bnd[0] < minx): minx = bnd[0]
  if (bnd[1] > maxy): maxy = bnd[1]
  if (bnd[2] > maxx): maxx = bnd[2]
  if (bnd[3] < miny): miny = bnd[3]

mosaicbounds = [minx, maxy, maxx, miny]
mosaicXsize = int((maxx - minx)/abs(Xres)) + 1
mosaicYsize = int((maxy - miny)/abs(Yres)) + 1

offsetsx = []
offsetsy = []

for bnd in listbounds:
  offsetsx.append(int(round((bnd[0]-minx)/abs(Xres))))
  offsetsy.append(int(round((maxy-bnd[1])/abs(Yres))))

full = np.zeros((mosaicYsize, mosaicXsize, listdatasets[0].RasterCount), dtype=np.int8)
blank = np.zeros((mosaicYsize, mosaicXsize, listdatasets[0].RasterCount), dtype=np.int8)

data1 = listdatasets[master].GetRasterBand(1)
full[offsetsy[master]:(offsetsy[master]+listdatasets[master].RasterYSize), offsetsx[master]:(offsetsx[master]+listdatasets[master].RasterXSize), 0] = \
  data1.ReadAsArray(0, 0, listdatasets[master].RasterXSize, listdatasets[master].RasterYSize)
data2 = listdatasets[master].GetRasterBand(2)
full[offsetsy[master]:(offsetsy[master]+listdatasets[master].RasterYSize), offsetsx[master]:(offsetsx[master]+listdatasets[master].RasterXSize), 1] = \
  data2.ReadAsArray(0, 0, listdatasets[master].RasterXSize, listdatasets[master].RasterYSize)
data3 = listdatasets[master].GetRasterBand(3)
full[offsetsy[master]:(offsetsy[master]+listdatasets[master].RasterYSize), offsetsx[master]:(offsetsx[master]+listdatasets[master].RasterXSize), 2] = \
  data3.ReadAsArray(0, 0, listdatasets[master].RasterXSize, listdatasets[master].RasterYSize)

## create geotransform of mosaic bounds
gt = listdatasets[0].GetGeoTransform()
newgt = tuple((minx, gt[1], np.double(0.0), maxy, np.double(0.0), gt[5]))

for j,bnd in enumerate(listbounds):
  if (j == master): continue

  blank.fill(0)

  data1 = listdatasets[j].GetRasterBand(1)
  blank[offsetsy[j]:(offsetsy[j]+listdatasets[j].RasterYSize), offsetsx[j]:(offsetsx[j]+listdatasets[j].RasterXSize), 0] = \
    data1.ReadAsArray(0, 0, listdatasets[j].RasterXSize, listdatasets[j].RasterYSize)
  data2 = listdatasets[j].GetRasterBand(2)
  blank[offsetsy[j]:(offsetsy[j]+listdatasets[j].RasterYSize), offsetsx[j]:(offsetsx[j]+listdatasets[j].RasterXSize), 1] = \
    data2.ReadAsArray(0, 0, listdatasets[j].RasterXSize, listdatasets[j].RasterYSize)
  data3 = listdatasets[j].GetRasterBand(3)
  blank[offsetsy[j]:(offsetsy[j]+listdatasets[j].RasterYSize), offsetsx[j]:(offsetsx[j]+listdatasets[j].RasterXSize), 2] = \
    data3.ReadAsArray(0, 0, listdatasets[j].RasterXSize, listdatasets[j].RasterYSize)

  b1data  = np.greater(blank[:,:,0], 0)
  b2data  = np.greater(blank[:,:,1], 0)
  b3data  = np.greater(blank[:,:,2], 0)
  b12data = np.logical_or(b1data, b2data)
  maskblank = np.logical_or(b12data, b3data)

  b1data  = np.greater(full[:,:,0], 0)
  b2data  = np.greater(full[:,:,1], 0)
  b3data  = np.greater(full[:,:,2], 0)
  b12data = np.logical_or(b1data, b2data)
  maskfull = np.logical_or(b12data, b3data)

  maskboth = np.logical_and(maskblank, maskfull)

  # full[mask] = blank[mask]

  for band in range(3):
    data1good = blank[:,:,band][maskboth].flatten()
    data2good = full[:,:,band][maskboth].flatten()

    minval = np.min(np.append(data1good, data2good))
    maxval = np.max(np.append(data1good, data2good))
    data1hist = np.histogram(data1good, bins=50, range=(minval, maxval))
    data2hist = np.histogram(data2good, bins=50, range=(minval, maxval))

    binscombo = data1hist[1]

    nPixels = np.sum(maskboth)

    cdf1 = []
    for k in range(0, len(data1hist[1])-1):
      b = np.sum(data1hist[0][:k]) 
      cdf1.append(float(b)/nPixels)

    cdf2 = []
    for m in range(0, len(data2hist[1])-1):
      g = np.sum(data2hist[0][:m]) 
      cdf2.append(float(g)/nPixels)

    zero = np.equal(blank[:,:,0], 0.0)

    im1 = np.interp(blank[:,:,band], binscombo[:-1], cdf1)
    im2 = np.interp(im1, cdf2, binscombo[:-1])
    im2[zero] = 0.0

    full[:,:,band][maskblank] = im2[maskblank]
  

driver = listdatasets[0].GetDriver()
outDs = driver.Create(outfile, mosaicXsize, mosaicYsize, listdatasets[0].RasterCount, datatype, [ 'INTERLEAVE=BIL' ]) 
outDs.SetGeoTransform(newgt)
outDs.SetProjection(raster_srs.ExportToWkt())
outBand = outDs.GetRasterBand(1)
outBand.WriteArray(full[:,:,0])
outBand.FlushCache()
outBand.SetNoDataValue(0)
outBand = outDs.GetRasterBand(2)
outBand.WriteArray(full[:,:,1])
outBand.FlushCache()
outBand.SetNoDataValue(0)
outBand = outDs.GetRasterBand(3)
outBand.WriteArray(full[:,:,2])
outBand.FlushCache()
outBand.SetNoDataValue(0)

del outDs, outBand

for ds in listdatasets:
  del ds
