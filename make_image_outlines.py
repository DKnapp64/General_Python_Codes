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

  ## create temporary output layer and Shapefile
  drv = ogr.GetDriverByName('MEMORY')
  tmpShapeDS = drv.CreateDataSource('memData')
  tmp = drv.Open('memData', 1)

  newField = ogr.FieldDefn('POLYNUM', ogr.OFTInteger)
  newField2 = ogr.FieldDefn('IMGNAME', ogr.OFTString)
  newField2.SetWidth(80)

  mysrs = osr.SpatialReference()
  mysrs.ImportFromWkt(inproj)
  tmp_layer = tmpShapeDS.CreateLayer("outlines", srs=mysrs)
  tmp_layer.CreateField(newField)
  tmp_layer.CreateField(newField2)

  ## create new output layer and Shapefile
  drv = ogr.GetDriverByName("ESRI Shapefile")
  dstDS = drv.CreateDataSource(outshape)
  dst_layer = dstDS.CreateLayer("outlines", srs=mysrs)
  dst_layer.CreateField(newField)
  dst_layer.CreateField(newField2)

  ## for each image, check data/nodata, polygonize it and write out shape
  imgIndex = 0

  for inraster in listit:
    inDS = gdal.Open(inraster, gdal.GA_ReadOnly)
    gt = inDS.GetGeoTransform()
    inproj = inDS.GetProjection()
    nodataval = inDS.GetRasterBand(1).GetNoDataValue()
    indata = inDS.GetRasterBand(1).ReadAsArray()
    if (nodataval is None):
      numzero = np.equal(indata, 0.0)
      if (np.sum(numzero) == 0):
       #  missing data value must be -9999
        nodataval = -9999.0
      else:
        nodataval = 0.0

    good = np.not_equal(indata, nodataval)

    mask = np.zeros_like(indata, dtype=np.dtype('B'))
    mask2 = np.zeros_like(indata, dtype=np.dtype('B'))
    mask[good] = 255
    mask2[good] = 1
    memdrv = gdal.GetDriverByName('MEM')
    tempDS = memdrv.Create('', mask.shape[1], mask.shape[0], 2, eType=gdal.GDT_Byte)
    tempDS.SetGeoTransform(gt)
    tempDS.SetProjection(inproj)
    tempDS.GetRasterBand(1).WriteArray(mask)
    tempDS.GetRasterBand(2).WriteArray(mask2)
    tempDS.GetRasterBand(1).SetNoDataValue(0)
    tempDS.GetRasterBand(2).SetNoDataValue(0)
    tempDS.FlushCache()
    myBand = tempDS.GetRasterBand(1)
    ## gdal.FillNodata(targetBand=myBand, maskBand=None, maxSearchDist=5, smoothingIterations=0)
    myMask = tempDS.GetRasterBand(2)
    ## gdal.FillNodata(targetBand=myMask, maskBand=None, maxSearchDist=5, smoothingIterations=0)
    gdal.Polygonize(myBand, myMask, tmp_layer, 0, [], callback=None)
    tmp_layer.ResetReading()
    imgIndex += 1

    ## for i in np.arange(0, tmp_layer.GetFeatureCount()):
    feat = tmp_layer.GetNextFeature()
    feat.SetField('POLYNUM', imgIndex)
    feat.SetField('IMGNAME', inraster)
    dst_layer.CreateFeature(feat)
    dstDS.FlushCache()
    tmp_layer.ResetReading()
    tmp_layer.DeleteFeature(0)

    tempDS = None
    inDS = None
    print(("Finished image %d") % (imgIndex))

  tmpShapeDS = None
  dstDS = None


if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ USAGE ] you must supply 2 arguments: make_image_outlines.py inpattern outshape")
    print("")
    sys.exit( 1 )

  main( sys.argv[1], sys.argv[2] )

