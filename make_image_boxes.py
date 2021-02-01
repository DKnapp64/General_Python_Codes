#!/bin/env python3
import numpy as np
import gdal
import ogr, osr
import os, sys
import numpy as np
import glob

def main(inpattern, outshape):

  listit = glob.glob(inpattern)

  print(("Found %d images") % (len(listit)))

  inDS = gdal.Open(listit[0], gdal.GA_ReadOnly)
  gt = inDS.GetGeoTransform()
  inproj = inDS.GetProjection()
  inDS = None

  newField = ogr.FieldDefn('POLYNUM', ogr.OFTInteger)
  newField2 = ogr.FieldDefn('IMGNAME', ogr.OFTString)
  newField2.SetWidth(80)

  mysrs = osr.SpatialReference()
  mysrs.ImportFromWkt(inproj)

  ## create new output layer and Shapefile
  drv = ogr.GetDriverByName("ESRI Shapefile")
  dstDS = drv.CreateDataSource(outshape)
  dst_layer = dstDS.CreateLayer("outlines", srs=mysrs)
  dst_layer.CreateField(newField)
  dst_layer.CreateField(newField2)
  layer_defn = dst_layer.GetLayerDefn()

  ## for each image, check data/nodata, polygonize it and write out shape
  imgIndex = 0

  for inraster in listit:
    inDS = gdal.Open(inraster, gdal.GA_ReadOnly)
    gt = inDS.GetGeoTransform()
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(gt[0], gt[3])
    ring.AddPoint(gt[0] + (inDS.RasterXSize * gt[1]), gt[3])
    ring.AddPoint(gt[0] + (inDS.RasterXSize * gt[1]), gt[3] + (inDS.RasterYSize * gt[5]))
    ring.AddPoint(gt[0], gt[3] + (inDS.RasterYSize * gt[5]))
    ring.CloseRings()
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    ##now lets write this into our layer/shape file:
    feat = ogr.Feature(layer_defn)
    feat.SetGeometry(poly)
    feat.SetFID(imgIndex)
    feat.SetField('POLYNUM', imgIndex)
    feat.SetField('IMGNAME', os.path.basename(inraster))
    dst_layer.CreateFeature(feat)
    poly, feat, ring, inDS = None, None, None, None
    imgIndex += 1 #increment feature index

  ## close the output shapefile
  dstDS.Destroy()


if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ USAGE ] you must supply 2 arguments: make_image_boxes.py inpattern outshape")
    print("")
    sys.exit( 1 )

  main( sys.argv[1], sys.argv[2] )

