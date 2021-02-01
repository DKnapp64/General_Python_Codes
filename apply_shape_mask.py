#!/bin/env python3
import numpy as np
import gdal, ogr, osr
import os, sys
import math
import glob

def main(inimagefile, inshape, nodata):
  """ apply_shape_mask.py
  This is the main function.  It takes an input Shapefile and an output image file
  and applies the polygonms in the shapefile as a mask
  image file.
  """

  root = os.path.basename(inimagefile)[0:15]
  ## newroot = root.replace('-','_')
  newroot = root
  temp = os.path.dirname(inimagefile)
  parts = temp.split(os.path.sep)
  week = parts[-1]
  inshapefull = '/data/gdcsdata/Research/Researcher/Knapp/Moorea_Weekly/Baseline_Cloud_masks/'+inshape
  inshapefile = glob.glob(inshapefull)
  if (len(inshapefile) == 0):
    print("Cannot find this Shapefile for this image in:\n %s\n Quitting" % (inshapefull))
    sys.exit(0)
  inshapefile = inshapefile[0]
  
  outmaskedimage = os.path.splitext(inimagefile)[0]+"_masked.tif"
  ## Open the input image file
  imgDS = gdal.Open(inimagefile, gdal.GA_ReadOnly)
  if imgDS is None:
    print("Error: Canonot open file %s" % (inimagefile))
    sys.exit(1)

  ## Get the projection of the image
  rasproj = imgDS.GetProjectionRef()

  ## Get the GeoTransform of the image
  ## the GeoTransform provides the upper left corner and pixel resolution
  ## information of the image
  gt = imgDS.GetGeoTransform()

  rxmin = gt[0]
  rxmax = gt[0] + (imgDS.RasterXSize * gt[1])
  rymin = gt[3] + (imgDS.RasterYSize * gt[5])
  rymax = gt[3] 

  ## put the image projection information into a Spatial Reference
  ## in order to get the EPSG projection code.
  myosr = osr.SpatialReference()
  myosr.ImportFromWkt(rasproj)

  ## get the raster projection's EPSG code
  rasepsg = int(myosr.GetAttrValue("AUTHORITY", 1))                       

  ##  Get the Shape driver from ogr.
  drvshp = ogr.GetDriverByName('ESRI Shapefile')
  ## drvkml = ogr.GetDriverByName('KML')
  ## Open the SHapefile with the Shapefile driver
  vecDS = drvshp.Open(inshapefile, 0)  ## 0 means read only, 1 mean writable

  if vecDS is None:
    print("Error: Cannot open file %s" % (inshapefile))
    imgDS = None
    sys.exit(1)

  ## get the layer in the Shapefile.  Usually, there is noyl one layer in a shapefile
  layer = vecDS.GetLayer()

  ## get the spatial reference of the vector Shapefile and get its EPSG code
  vecsrs = layer.GetSpatialRef()
  vecepsg = int(vecsrs.GetAttrValue("AUTHORITY", 1))

  ## if the EPSG codes are not the same, then the projections are not the same.
  ## Advise the user of this and exit.
  if (rasepsg != vecepsg):
    print("Projection of Vector file is not the same as raster file")
    print("Please use ogr2ogr to create a version of the Shapefile in the ")
    print("same projection as the Image file")
    imgDS, vecDS = None, None
    print("Raster: %d    Shape: %d" % (rasepsg, vecepsg))
    sys.exit(1)

  ## There should only be one feature with the geometry of the area to cover.
  ## Get the feature count and the feature.
  featcnt = layer.GetFeatureCount()

  # Rasterize zone polygon to a raster
  # Create memory target raster
  ## targetDS = gdal.GetDriverByName('MEM').Create('', imgDS.RasterXSize, imgDS.RasterYSize, 1, gdal.GDT_Byte)
  targetDS = gdal.GetDriverByName('MEM').Create('', imgDS.RasterXSize, imgDS.RasterYSize, 1, gdal.GDT_Byte)
  targetDS.SetGeoTransform(gt)                                                                          

  # Create for target raster the same projection as for the value raster      
  raster_srs = osr.SpatialReference()                                         
  raster_srs.ImportFromWkt(imgDS.GetProjectionRef())
  targetDS.SetProjection(raster_srs.ExportToWkt())
                                                                                
  # Rasterize polygon to raster
  gdal.RasterizeLayer(targetDS, [1], layer, burn_values=[1])

  ## Get the rasterized polygon data and count the number of pixels.
  ## Because we set the value in the raster to 1, we should be able to simply sum them up.
  polytemp = targetDS.GetRasterBand(1).ReadAsArray()

  mask = np.greater(polytemp, 0)

  outDS = gdal.GetDriverByName('GTiff').Create(outmaskedimage, imgDS.RasterXSize, imgDS.RasterYSize, imgDS.RasterCount, imgDS.GetRasterBand(1).DataType, options=['COMPRESS=LZW'])
  outDS.SetGeoTransform(gt)

  # Create for target raster the same projection as for the value raster
  outDS.SetProjection(raster_srs.ExportToWkt())

  for band in range(imgDS.RasterCount):
    bandarr = imgDS.GetRasterBand(band+1).ReadAsArray()
    bandarr[mask] = nodata
    outDS.GetRasterBand(band+1).WriteArray(bandarr)
    outDS.GetRasterBand(band+1).SetNoDataValue(-9999)

  outDS.FlushCache()

  ## close all 3 data sets by setting them to None
  imgDS, vecDS, targetDS, outDS = None, None, None, None

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ USAGE ] you must supply 3 arguments: apply_shape_mask.py inimgfile inshape nodatavalue")
    print("inimgfile - the image file ")
    print("inshape - the shape file ")
    print("nodatavalue - value to place in masked areas ")
    sys.exit( 0 )
  main( sys.argv[1], sys.argv[2], int(sys.argv[3]) )

