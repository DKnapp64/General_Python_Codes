#!/bin/env python3
import gdal
import ogr, osr
import numpy as np
import os, sys
import math

def main(inimg, inpolyshp, outpointshp):

  ## if the image file exists, open it and get GeoTransform
  ## otherwise, exit
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

  ## Open the input Shape Polygon File and get its field definitions
  shpDS = ogr.GetDriverByName("ESRI Shapefile").Open(inpolyshp)  
  layer = shpDS.GetLayer()
  featCnt = layer.GetFeatureCount() 
  layerDefn = layer.GetLayerDefn()
  fielddefs = []
  for n in range(layerDefn.GetFieldCount()):
    fdefn = layerDefn.GetFieldDefn(n)
    fielddefs.append(fdefn)

  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt(inDS.GetProjection())                            

  driver = ogr.GetDriverByName('ESRI Shapefile')
  outDS = driver.CreateDataSource(outpointshp)
  outlayer = outDS.CreateLayer('crownpoints', raster_srs, ogr.wkbPoint)
  outlayer_defn = outlayer.GetLayerDefn() # gets parameters of the current shapefile
  for n in range(layerDefn.GetFieldCount()):
    idDefn = ogr.FieldDefn(fielddefs[n].name, fielddefs[n].type)
    outlayer.CreateField(idDefn)

  featureIndex = 0

  for thisFeat in range(featCnt):
    ## fidlist = feat.GetAttribute('CODE')
    layer.SetAttributeFilter(' FID = %d ' % (thisFeat))
    feat = layer.GetFeature(thisFeat)
    geom = feat.GetGeometryRef() 
    envel = geom.GetEnvelope()
    ulx = math.floor(envel[0]/xres) * xres 
    uly = math.ceil(envel[3]/yres) * yres 
    lrx = math.ceil(envel[1]/xres) * xres 
    lry = math.floor(envel[2]/yres) * yres 
    rastxsize = int((lrx - ulx)/xres) + 1
    rastysize = int((lry - uly)/yres) + 1
    targetDS = gdal.GetDriverByName('MEM').Create('', rastxsize, rastysize, 1, gdal.GDT_Int16)
    targetDS.SetProjection(inDS.GetProjection()) 
    newgt = (ulx, gt[1], 0, uly, 0, gt[5]) 
    targetDS.SetGeoTransform(newgt)
    gdal.RasterizeLayer(targetDS, [1], layer, burn_values=[thisFeat+1])

    fidlist = feat.GetFID()
    targetDS.FlushCache()
    inside = targetDS.ReadAsArray()
    good = np.equal(inside, thisFeat+1)
    ## index = np.equal(mask, thisFeat)
    index = np.nonzero(good)
    numpixels = np.sum(good)
    print('NumPixels: %d %d' % (numpixels, fidlist))
    if (numpixels > 0):
      xcoords = newgt[0] + ((index[1] + 0.5) * newgt[1]) 
      ycoords = newgt[3] + ((index[0] + 0.5) * newgt[5]) 

    targetDS = None

    for j in range(numpixels):
      point = ogr.Geometry(ogr.wkbPoint)
      point.AddPoint(xcoords[j], ycoords[j])

      ##now lets write this into our layer/shape file:
      feature = ogr.Feature(layerDefn)
      feature.SetGeometry(point)
      feature.SetFID(featureIndex)
      for n in range(layerDefn.GetFieldCount()):
        feature.SetField(fielddefs[n].name, feat.GetField(fielddefs[n].name))

      outlayer.CreateFeature(feature)
      featureIndex += 1
      layer.SetAttributeFilter('')

  shpDS, layer, outlayer = None, None, None
  inDS, outDS = None, None

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ ERROR ] you must supply 3 arguments: poly2points.py inimg inpolyshp outpointshp")
    print("where:")
    print("    inimg = input image.")
    print("    inpolyshp = input polygon shapefile.")
    print("    outpntshp = output point shape file.")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3] )
