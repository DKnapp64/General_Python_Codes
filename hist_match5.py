#!/bin/env python2
import numpy as np
import gdal, ogr, osr
from scipy.interpolate import interp1d
import sys
import matplotlib.pyplot as plt

def main( dimac1file, dimacref, dimacout ):
  
  ########################################################
  # Open data
  ########################################################

  ds1 = gdal.Open(dimac1file)
  ds2 = gdal.Open(dimacref)
  
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
  else:
    print("Files do not intersect with data")
    exit()
  
  driver = ds1.GetDriver()
  outDs = driver.Create(dimacout, ds1.RasterXSize, ds1.RasterYSize, ds1.RasterCount, datatype, [ 'INTERLEAVE=BIL' ]) 
  outDs.SetGeoTransform(gt1)
  outDs.SetProjection(raster_srs.ExportToWkt())
  
  ## make masks
  temp1 = ds1.ReadAsArray(px1[0], px1[1], px1[2]-px1[0], px1[3]-px1[1])
  temp2 = ds2.ReadAsArray(px2[0], px2[1], px2[2]-px2[0], px2[3]-px2[1])
  sumit1 = np.sum(temp1, axis=0)
  sumit2 = np.sum(temp2, axis=0)
  good = np.logical_and(sumit1 > 0, sumit2 > 0)

  ## overlapgt = tuple((max(r1[0], r2[0]), gt1[1], 0, min(r1[1], r2[1]), 0, gt1[5]))

  ## pdb.set_trace()

  ## driver = ds1.GetDriver()
  ## tempDs = driver.Create('tempmask', good.shape[1], good.shape[0], 1, datatype)
  ## tempDs.SetGeoTransform(overlapgt)
  ## tempDs.SetProjection(raster_srs.ExportToWkt())
  ## tempBand = tempDs.GetRasterBand(1)
  ## tempBand.WriteArray(good.astype(np.uint8))
  ## tempBand.FlushCache()
   
  ## del temp1, temp2, sumit1, sumit2, tempDs

  # Read raster as arrays
  for band in range(ds1.RasterCount):
    data1 = ds1.GetRasterBand(band+1)
    dataarray1 = data1.ReadAsArray(px1[0], px1[1], px1[2]-px1[0], px1[3]-px1[1])
    data2 = ds2.GetRasterBand(band+1)
    dataarray2 = data2.ReadAsArray(px2[0], px2[1], px2[2]-px2[0], px2[3]-px2[1])
  
    # find good data
    data1good = dataarray1[good].flatten()
    data2good = dataarray2[good].flatten()

    ## diff = np.mean(data1good) - np.mean(data2good)
    ## print ("Pre-normalization Band %d: %5f") % (band+1, diff)
  
    minval = np.min(np.append(data1good, data2good))
    maxval = np.max(np.append(data1good, data2good))

    data1hist = np.histogram(data1good, bins=256, range=(minval, maxval), normed=False)
    data2hist = np.histogram(data2good, bins=256, range=(minval, maxval), normed=False)
  
    binscombo = data2hist[1]
  
    nPixels = np.sum(good)
  
    cdf1 = []
    for k in range(0, len(data1hist[1])-1):
      b = np.sum(data1hist[0][:k])
      cdf1.append(255 * float(b)/nPixels)
  
    cdf2 = []
    for j in range(0, len(data2hist[1])-1):
      g = np.sum(data2hist[0][:j])
      cdf2.append(255 * float(g)/nPixels)

    datafull1 = ds1.GetRasterBand(band+1)
    datafull1Band = datafull1.ReadAsArray(0, 0, ds1.RasterXSize, ds1.RasterYSize)
    zero = np.equal(datafull1Band, 0.0)
  
    im1 = np.interp(datafull1Band, data1hist[1][:-1], cdf1)
    im2 = np.interp(im1, cdf2, data2hist[1][:-1])
    im2[zero] = 0.0

    hold = im2[px1[1]:px1[3],px1[0]:px1[2]][good]
    holdhist = np.histogram(hold, 256, normed=False)

    cdfhold = []
    for i in range(0, len(holdhist[1])-1): 
      d = np.sum(holdhist[0][:i])
      cdfhold.append(255 * float(d)/nPixels)
     
    plt.plot(binscombo[:-1], cdf1, 'r')
    plt.plot(binscombo[:-1], cdf2, 'g')
    plt.plot(binscombo[:-1], cdfhold, 'k')
    plt.show()

    outBand = outDs.GetRasterBand(band+1)
    outBand.WriteArray(im2.astype(np.uint8))
    outBand.FlushCache()
    outBand.SetNoDataValue(0)
  
    del im2, im1, outBand
  
  del outDs, ds1, ds2

if __name__ == "__main__":
  
  if len( sys.argv ) != 4:
    print "[ USAGE ] you must supply 3 arguments: hist_match5.py dimacinput dimacreference dimachistmatched"
    print "                            where:"
    print "                               dimacinput = the input DiMAC image to be adjusted"
    print "                               dimacreference = the partially overlapping image that is the reference source to match to"
    print "                               dimachistmatched = the output matched image"
    print ""
    print ""
    print ""
    sys.exit( 0 )
  
  print main( sys.argv[1], sys.argv[2], sys.argv[3] )

