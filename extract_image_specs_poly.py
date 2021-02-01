#!/bin/env python3
import gdal
import ogr, osr
import numpy as np
import os, sys
import math

def main(inimg, inmask, inshp, ndvithresh, outtxt):

  red = 680
  nir = 800

  if os.path.exists(inimg):
    inDS = gdal.Open(inimg, gdal.GA_ReadOnly)
    gt = inDS.GetGeoTransform()
    ulx = gt[0]
    uly = gt[3]
    xres = gt[1]
    yres = gt[5]
  else:
    print('File %s does not exist' % (inimg))
    sys.exit(0)

  metdata = inDS.GetMetadata('ENVI') 
  waves = np.array(metadata['wavelength'].strip('{}').split(','), dtype=np.float)
  red = np.argmin(np.abs(waves-680))
  nir = np.argmin(np.abs(waves-800))

  if os.path.exists(inmask):
    mDS = gdal.Open(inmask, gdal.GA_ReadOnly)
  else:
    print('File %s does not exist' % (inmask))
    inDS = None
    sys.exit(0)

  barraylist = []
  for b in range(inDS.RasterCount):
    theband = inDS.GetRasterBand(b+1)
    barraylist.append(theband)
 
  shpDS = ogr.GetDriverByName("ESRI Shapefile").Open(inshp)  
  layer = shpDS.GetLayer()
  featCnt = layer.GetFeatureCount() 

  f = open(outtxt, 'w')

  targetDS = gdal.GetDriverByName('MEM').Create('', inDS.RasterXSize, inDS.RasterYSize, 1, gdal.GDT_Byte)
  raster_srs = osr.SpatialReference()                                           
  raster_srs.ImportFromWkt(inDS.GetProjection())                            
  targetDS.SetProjection(raster_srs) 

  for thisFeat in range(featCnt):
    feat = layer.GetNextFeature()  
    ## thename = (feat.GetField("specname"))[0:9]
    geom = feat.GetGeometryRef() 
    extent = geom.GetEnvelope()
    pixmin = int(math.floor((extent[0] - ulx)/xres))
    pixmax = int(math.floor((extent[1] - ulx)/xres))
    linmin = int(math.floor((extent[2] - uly)/yres))
    linmax = int(math.floor((extent[3] - uly)/yres))
    gdal.RasterizeLayer(targetDS, [1], layer, burn_values=[1])
    mask = targetDS.GetRasterBand(1).ReadAsArray(pixmin, linmin, pixmax-pixmin, linmax-linmin).astype(np.bool)
    numpixels = np.sum(mask)
    index = np.nonzero(mask)
    if (numpixels > 0):
      data = targetDS.ReadAsArray(pixmin, linmin, pixmax-pixmin, linmax-linmin)
      ndvi = (data[:,:,nir] - data[:,:,red]).astype(np.float)/(data[:,:,nir] + data[:,:,red])
      bigstring = ("%d, %s, ") % (thisFeat, inimg)
      for n in range(numpixels):
        thespec = np.squeeze(data[index[n,0], index[n,1], :])
        thendvi = np.squeeze(ndvi[index[n,0], index[n,1]])
        if (thendvi < ndvithresh):
          continue
        for b in range(inDS.RasterCount-1):
          bigstring += "%8.4f," % (thespec[n]/10000.0) 
        bigstring += "%8.4f\n" % (thespec[n]/10000.0) 
        f.write(bigstring)
    else:
      print("This image is not covered by polygon %d of %d" % (thisFeat, featCnt))

  for band in barraylist:
    band = None  

  shpDS, layer = None, None 
  inDS, targetDS = None, None
  f.close()

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ ERROR ] you must supply 3 arguments: extract_image_specs_poly.py inimg inshp outtxt")
    print("where:")
    print("    inimg = input image.")
    print("    inshp = input polygon shapefile.")
    print("    outtxt = output text file with extracted spectral values from image for each point in the shapefile.")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3] )
