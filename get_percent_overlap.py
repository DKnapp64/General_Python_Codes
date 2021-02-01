#!/bin/env python3
import gdal
import ogr
import osr
import numpy as np
import os, sys
import math

def get_overlap_info(focal_bounds, focal_res, img_bounds, img_res):

  """ get_overlap_info:
      This is a python function for giving the bounds of an area of interest (Focal) and comparing
      to an image bounds.  It returns the upper left column and row and the number of columns and rows
      based on the resolutions of both the Focal and Img spaces.

      Both focal and image bounds inputs must be in the same coordinate system being
      Xmin, Xmax, Ymin, Ymax
  """

  ##                X_min      X_max     Y_min     Y_max
  ## Bounding Box: 436933.02 449804.48 1922102.98 1928663.29 
  ## find bounds of images
  ## r1 = [new_geo[0], new_geo[3], new_geo[0] + (new_geo[1] * dest.RasterXSize), new_geo[3] + (new_geo[5] * dest.RasterYSize)]
  ## r2 = [gt2[0], gt2[3], gt2[0] + (gt2[1] * img2.RasterXSize), gt2[3] + (gt2[5] * img2.RasterYSize)]

  r1 = [focal_bounds[0], focal_bounds[3], focal_bounds[1], focal_bounds[2]]
  r2 = [img_bounds[0], img_bounds[3], img_bounds[1], img_bounds[2]]

  ## find intersection
  intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]
  testx = intersection[2]-intersection[0]
  testy = intersection[1]-intersection[3]
  if (testx < 0) or (testy < 0):
    return((-9999,-9999,-9999,-9999), (-9999,-9999,-9999,-9999))                

  # check for any overlap
  left1flt = (intersection[0]-r1[0])/focal_res # difference divided by pixel dimension
  left1 = int(np.abs(round((intersection[0]-r1[0])/focal_res))) # difference divided by pixel dimension
  top1flt = (intersection[1]-r1[1])/focal_res
  top1 = int(np.abs(round(((intersection[1]-r1[1])/focal_res))))
  col1 = int(np.abs(round(((intersection[2]-r1[0])/focal_res) - left1flt))) # difference minus offset left
  row1 = int(np.abs(round(((intersection[3]-r1[1])/focal_res) - top1flt)))

  left2flt = (intersection[0]-r2[0])/img_res # difference divided by pixel dimension
  left2 = int(np.abs(round(((intersection[0]-r2[0])/img_res)))) # difference divided by pixel dimension
  top2flt = (intersection[1]-r2[1])/img_res
  top2 = int(np.abs(round(((intersection[1]-r2[1])/img_res))))
  col2 = int(np.abs(round(((intersection[2]-r2[0])/img_res) - left2flt))) # difference minus new left offset
  row2 = int(np.abs(round(((intersection[3]-r2[1])/img_res) - top2flt)))

  return((left1,top1,col1,row1), (left2,top2,col2,row2))

def main(inshapefile, inimagefile):
  """ get_percent_overlap.py
  This is the main function.  It takes an input Shapefile and an output image file
  and returns the percentage of the Shape are that is covered by data from the
  image file.
  """

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
  feat = layer.GetFeature(0)   ## assume that there is only 1 feature/polygon in the shapefile

  ## Get the geometry of the feature.  That is, the polygon that encloses the area.
  geom = feat.GetGeometryRef()

  ## Get the envelope of the area, which contains the min and max in the X and Y dimensions.
  envelope = geom.GetEnvelope()

  ## Recalculate the min and max so that they are even multiples of the resolution.
  xmin = math.floor(envelope[0]/gt[1]) * gt[1]
  xmax = math.ceil(envelope[1]/gt[1]) * gt[1]
  ymin = math.floor(envelope[2]/gt[1]) * gt[1]
  ymax = math.ceil(envelope[3]/gt[1]) * gt[1]

  ## Determine the size of the output space
  xcount = int((xmax - xmin)/gt[1])
  ycount = int((ymax - ymin)/gt[1])

  # Rasterize zone polygon to a raster
  # Create memory target raster
  targetDS = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
  targetDS.SetGeoTransform((xmin, gt[1], 0, ymax, 0, gt[5]))                                                                          

  # Create for target raster the same projection as for the value raster      
  raster_srs = osr.SpatialReference()                                         
  raster_srs.ImportFromWkt(imgDS.GetProjectionRef())
  targetDS.SetProjection(raster_srs.ExportToWkt())
                                                                                
  # Rasterize polygon to raster                                          
  gdal.RasterizeLayer(targetDS, [1], layer, burn_values=[1])

  ## Get the rasterized polygon data and count the number of pixels.
  ## Because we set the value in the raster to 1, we should be able to simply sum them up.
  polytemp = targetDS.GetRasterBand(1).ReadAsArray()

  ## Calculate the total size of the polygon.
  polysize = np.sum(polytemp)

  ## find the overlap between the polygon raster and the Dove image.
  focalbnd, imagebnd = get_overlap_info((xmin, xmax, ymin, ymax), 3.0, (rxmin, rxmax, rymin, rymax), 3.0)

  ## use those bounds to extract the same area from both.
  polypart = targetDS.GetRasterBand(1).ReadAsArray(focalbnd[0], focalbnd[1], focalbnd[2], focalbnd[3])
  imgpart = imgDS.GetRasterBand(1).ReadAsArray(imagebnd[0], imagebnd[1], imagebnd[2], imagebnd[3])

  ## Find the pixels that are both inside the polygon and have valid image data (pixels greaterthan 0).
  overlap = np.logical_and(np.equal(polypart, 1), np.greater(imgpart, 0))

  ## sum that overlap area and divide by total size to get percent coverage.
  numover = np.sum(overlap)
  outpercent = (float(numover)/float(polysize)) * 100.0
  print("Percent overlap is: %0.1f" % (outpercent))
  
  ## close all 3 data sets by setting them to None
  imgDS, vecDS, targetDS = None, None, None

if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ USAGE ] you must supply 2 arguments: get_percent_overlap.py inshapefile inimgfile")
    print("inshapefile - the shapefile whose percent coverage from the image we want to find ")
    print("inimgfile - the image file ")
    sys.exit( 0 )
  main( sys.argv[1], sys.argv[2] )

