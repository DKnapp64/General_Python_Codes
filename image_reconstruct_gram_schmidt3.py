#!/bin/env python2
import numpy as np
import gdal, osr
import sys

vswirfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch44_20170930_test3_rb_img'
dicamfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch44_20170930_update20171027_dimac_match'
maskfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch44_20170930_rb_mask'
hyperfile = 'patch44_20170930_nearest_hybrid_rb'

def qr_by_gram_schmidt(A):
  m, n = np.shape(A)
  Q = np.zeros((m, n))
  R = np.zeros((n, n))
  for j in xrange(n):
    v = A[:,j]
    for i in xrange(j-1):
      q = Q[:,i]
      R[i,j] = q.dot(v)
      v = v - R[i, j] * q
    norm = np.linalg.norm(v)
    Q[:,j] = v / norm
    R[j,j] = norm
  return Q, R

## according to various references, Q * R (via matrix multiplication) equals the original inPUT  matrix.
## Thus, if we substitute in the adjusted gray-scale DiMAC data to look like the first GRam-Schmidt
## component (Q[:,0]), we should just have to do np.matmul(Q, R) to get the new fused image data.
## 
## A = np.random.rand(13,10) * 1000
## Q, R = qr_by_gram_schmidt(A)
## Q.shape, R.shape
## np.abs((A - Q.dot(R)).sum()) < 1e-6

########################################################
# Open data
vswir = gdal.Open(vswirfile)
mask = gdal.Open(maskfile)
dicam = gdal.Open(dicamfile)

ratio = np.double(10)

geotrans = dicam.GetGeoTransform()

xoff = 0
yoff = 0
xcountvswir = vswir.RasterXSize
ycountvswir = vswir.RasterYSize
xcountdicam = dicam.RasterXSize
ycountdicam = dicam.RasterYSize

# Read raster as arrays
vswirdata = vswir.ReadAsArray(xoff, yoff, xcountvswir, ycountvswir).astype(np.float)
## vswirdata = np.kron(vswirdata, np.ones((1,10,10))).astype(np.float)
dicamdata = dicam.ReadAsArray(xoff, yoff, xcountdicam, ycountdicam).astype(np.float)
dicamdata = np.mean(dicamdata, axis=0)
dicamcoarse = np.zeros((ycountvswir, xcountvswir), dtype=np.float)

print "Arrays have been read, dicamcoarse created\n"

for j in range(ycountvswir):
  for k in range(xcountvswir):
    dicamcoarse[j,k] = np.mean(dicamdata[np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
      np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)])

maskdata = mask.ReadAsArray(xoff, yoff, xcountvswir, ycountvswir)
good = np.equal(maskdata, 1)   # good data on patch reef, byte value of 1
print "Mask read and good array created\n"

## make index and get only the good pixels (i.e., on the patch reef)
row, col = np.indices(good.shape)
row = row[good]
col = col[good]
dicamcoarsegood = dicamcoarse[row, col]

checkers = np.arange(1, (xcountvswir*ycountvswir)+1).reshape(ycountvswir, xcountvswir)
checkers100 = np.kron(checkers, np.ones((10,10))).astype(np.int64)
goodbig = np.kron(good, np.ones((10,10))).astype(bool)

checkers100good = checkers100[goodbig]
sortindex = np.argsort(checkers100good)
rowbig, colbig = np.indices(goodbig.shape)

rowbig = rowbig[goodbig].flatten()
colbig = colbig[goodbig].flatten()
rowbig = rowbig[sortindex]
colbig = colbig[sortindex]

np.savez("rowcolhold.npz", row=row, col=col, rowbig=rowbig, colbig=colbig)

print "vswirdata shape: %d, %d, %d\n" % (vswirdata.shape[0], vswirdata.shape[1], vswirdata.shape[2])

vswirgood = vswirdata[:, row, col]
print "vswirgood shape: %d, %d\n" % (vswirgood.shape[0], vswirgood.shape[1])

dicamdata = dicamdata[rowbig, colbig]
print "dicamdata shape: %d\n" % dicamdata.shape
print "dicamcoarsegood shape: %d\n" % dicamcoarsegood.shape

## concatenate the coarsened Pan (DiMAC) band to the rest of the data.
comboarr = np.concatenate((dicamcoarsegood.reshape(1, vswirgood.shape[1]), vswirgood))
print "comboarr shape: %d, %d\n" % comboarr.shape
 
## transpose so that the 52 wavelengths (53 bands with the Pan) are in the columns
## and each good pixel of data is in the rows
comboarr = comboarr.T
print "comboarr NEW shape: %d, %d\n" % comboarr.shape

myQ, myR = qr_by_gram_schmidt(comboarr)
print "Finished making myQ and myR\n"

myQ100 = np.kron( myQ, np.ones((100,1)))
print "Expanded myQ100 size: %d, %d\n" % myQ100.shape
print "myR size: %d, %d\n" % myR.shape

## np.savez("datahold.npz", comboarr=comboarr, row=row, col=col, dicamdata=dicamdata, good=good, myQ=myQ, myR=myR)
## print "Finished Saving data to a NPZ file\n"

## make histogram of 1st band, get mean and stdev
myQmean = np.mean(myQ[:,0])
myQstdev = np.std(myQ[:,0])

print "Finished making myQ and myR\n"
print "Mean: %f\n" % (myQmean)
print "StDev.: %f\n" % (myQstdev)

dicammean = np.mean(dicamdata)
dicamstdev = np.std(dicamdata)

## take DiMAC data and make it look like distribution of first GRam-Schmidt component of myQ
print "Making new distribution for first component of Q\n"
newvals = (((dicamdata - dicammean) / dicamstdev) * myQstdev) + myQmean

## substitute adjusted high resolution DiMAC data for first G-S component
myQ100[:,0] =  newvals
print "Substitution done\n"
del dicamdata, myQ, vswirdata, vswirgood, comboarr
print "Deleted unneeded data from memory\n"

outdata = myQ100.dot(myR)
print "Finished matrix multiplication for reversing Gram-Schmidt\n"
print "outdata size: %d, %d\n" % outdata.shape

# Create for target raster the same projection as for the value raster
driver = gdal.GetDriverByName('ENVI')
target_ds = driver.Create(hyperfile, xcountdicam, ycountdicam, vswir.RasterCount, gdal.GDT_Float32)
raster_srs = osr.SpatialReference()
raster_srs.ImportFromWkt(vswir.GetProjectionRef())
target_ds.SetProjection(raster_srs.ExportToWkt())
target_ds.SetGeoTransform(geotrans)

hypercam = np.zeros((ycountdicam,xcountdicam), dtype=np.float32)
print "Writing out fused image\n"

for c in range(vswir.RasterCount):
  ## must add 1 to c to skip the inserted pan band from outdata and only get the fused 52 wavelengths 
  hypercam[rowbig, colbig] = outdata[:,c+1]
  target_ds.GetRasterBand(c+1).WriteArray(hypercam)

del target_ds
del vswir, dicam, hypercam
