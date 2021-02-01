#!/bin/env python3
import numpy as np
import gdal
import ogr, osr
import os, sys
import davektools as dk

def main(inpix, outshape):
## inraster = "/Carnegie/DGE/caodata/Scratch/dknapp/Fish/coral_keahou_mosaic_v1k_dep_masked"
## outshape = "/Carnegie/DGE/caodata/Scratch/dknapp/Fish/coral_keahou_mosaic_v1k_dep_masked.shp"

  inDS = gdal.Open(inpix, gdal.GA_ReadOnly)
  mapstuff = dk.read_envi_hdr(inpix+'.hdr')
  gt = (mapstuff[0], mapstuff[2], 0, mapstuff[1], 0, mapstuff[3])
  ## gt = inDS.GetGeoTransform()
  insrs = osr.SpatialReference()
  if (mapstuff[4] > 0):
    insrs.ImportFromEPSG(32600+mapstuff[4])
  else: 
    insrs.ImportFromEPSG(32700+abs(mapstuff[4]))
  ## inproj = inDS.GetProjection()
  nodataval = inDS.GetRasterBand(1).GetNoDataValue()
  indata = inDS.GetRasterBand(1).ReadAsArray()
  if (nodataval is None):
    numzero = np.equal(indata, 0.0)
    if (np.sum(numzero) == 0):
      #  missing data value must be -9999 
      nodataval = -9999.0
    else: nodataval = 0.0
  
  good = np.not_equal(indata, nodataval)
  
  mask = np.zeros_like(indata, dtype=np.dtype('B'))
  mask2 = np.zeros_like(indata, dtype=np.dtype('B'))
  mask[good] = 255
  mask2[good] = 1
  memdrv = gdal.GetDriverByName('MEM')
  tempDS = memdrv.Create('', mask.shape[1], mask.shape[0], 2, eType=gdal.GDT_Byte)
  tempDS.SetGeoTransform(gt)
  tempDS.SetProjection(insrs.ExportToWkt())
  tempDS.GetRasterBand(1).WriteArray(mask)
  tempDS.GetRasterBand(2).WriteArray(mask2)
  tempDS.GetRasterBand(1).SetNoDataValue(0)
  tempDS.GetRasterBand(2).SetNoDataValue(0)
  tempDS.FlushCache()
  myBand = tempDS.GetRasterBand(1)
  gdal.FillNodata(targetBand=myBand, maskBand=None, maxSearchDist=5, smoothingIterations=0)
  myMask = tempDS.GetRasterBand(2)
  gdal.FillNodata(targetBand=myMask, maskBand=None, maxSearchDist=5, smoothingIterations=0)
  
  drv = ogr.GetDriverByName("ESRI Shapefile")
  dstDS = drv.CreateDataSource(outshape)
  ## mysrs = osr.SpatialReference()
  ## mysrs.ImportFromWkt(inproj)
  dst_layer = dstDS.CreateLayer("outline", srs=insrs)
  newField = ogr.FieldDefn('MYFIELD', ogr.OFTInteger)
  newField2 = ogr.FieldDefn('FLIGHT', ogr.OFTString)
  newField2.SetWidth(80)
  dst_layer.CreateField(newField)
  dst_layer.CreateField(newField2)
  gdal.Polygonize(myBand, myMask, dst_layer, 0, [], callback=None)
  ## dst_layer.FlushCache() 
  dst_layer.ResetReading() 

  print(inpix, dst_layer.GetFeatureCount())
  for i in range(0, dst_layer.GetFeatureCount()):
    feat = dst_layer.GetNextFeature()
    dst_layer.SetFeature(feat)
    feat.SetField(newField2.GetNameRef(), inpix)
    dst_layer.SetFeature(feat)
  
  dstDS.Destroy()
  tempDS = None
  inDS = None
  ## mysrs.MorphToESRI()
  ## f = open(inpix+'.prj', 'w')
  ## f.write(mysrs.ExportToWkt())
  ## f.close()
  
if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ USAGE ] you must supply 2 arguments: make_data_nodata_poly_pix.py inpix outshape")
    print("")
    sys.exit( 1 )

  main( sys.argv[1], sys.argv[2] )
