#!/bin/env python3
import os, sys
import ogr, osr
import pyproj
import numpy as np
import math

def main(inshp, outshp):

  if not os.path.exists(inshp):
    print('File %s does not exist' % (inshp))
    sys.exit(0)

  pseudomerc = pyproj.Proj('epsg:3857')

  vecDS = ogr.Open(inshp)                                                     
  lyr = vecDS.GetLayer()                                                        
  lyrdefn = lyr.GetLayerDefn()
  fieldcnt = lyrdefn.GetFieldCount()
  sourceSR = lyr.GetSpatialRef()

  tempfeat = lyr.GetNextFeature()
  tmpgeom = tempfeat.GetGeometryRef()

  if (tmpgeom.GetGeometryName() != 'POINT'):
    print('This is not a Point shapefile: %s' % (tmpgeom.GetGeometryName()))
    vecDS.Destroy()
    sys.exit(0)

  lyr.ResetReading()

  fieldname = []
  fieldtypecode = []
  fieldtype = []
  fieldwidth = []
  fieldprecision = []

  for j in range(fieldcnt):
    fieldname.append(lyrdefn.GetFieldDefn(j).GetName())
    fieldtypecode.append(lyrdefn.GetFieldDefn(j).GetType())
    fieldtype.append(ogr.GetFieldTypeName(fieldtypecode[j]))
    fieldwidth.append(lyrdefn.GetFieldDefn(j).GetWidth())
    fieldprecision.append(lyrdefn.GetFieldDefn(j).GetPrecision())
    print(fieldname[j], fieldtypecode[j], fieldtype[j], fieldwidth[j], fieldprecision[j])

  fieldtypecode[0] = 0
  fieldtype[0] = 'Integer'
  fieldwidth[0] = 5
  fieldprecision[0] = 0
  fieldtypecode[2] = 0
  fieldtype[2] = 'Integer'
  fieldwidth[2] = 5
  fieldprecision[2] = 0
  fieldtypecode[45] = 0
  fieldtype[45] = 'Integer'
  fieldwidth[45] = 5
  fieldprecision[45] = 0
  fieldtypecode[48] = 0
  fieldtype[48] = 'Integer'
  fieldwidth[48] = 5
  fieldprecision[48] = 0

  ## fieldname = fieldname[2:]
  ## fieldtypecode = fieldtypecode[2:]
  ## fieldtype = fieldtype[2:]
  ## fieldwidth = fieldwidth[2:]
  ## fieldprecision = fieldprecision[2:]

  print('--------------------------------------------------')
  for k in range(len(fieldname)):
    print(fieldname[k], fieldtype[k], fieldtypecode[k], fieldwidth[k], fieldprecision[k])
  print('--------------------------------------------------')

  ## create array of 12 offsets to get a 25-meter diameter circle around each
  ## center point
  circpnts = []
  for i in np.arange(0, 12):
    y0 = 12.5 * math.cos((i*30.0)*math.pi/180.) 
    x0 = 12.5 * math.sin((i*30.0)*math.pi/180.)
    circpnts.append([x0, y0])
  circpnts = np.asarray(circpnts)

  ## Create output Shapefile
  mysrs = osr.SpatialReference()                                                
  mysrs.ImportFromEPSG(3857)
                                                                                
  ## create new output layer and Shapefile                                      
  drv = ogr.GetDriverByName("ESRI Shapefile")                                   
  dstDS = drv.CreateDataSource(outshp)                                        
  dst_layer = dstDS.CreateLayer("footprints", srs=mysrs)                          

  for j in range(fieldcnt):
    newField = ogr.FieldDefn(fieldname[j], fieldtypecode[j])
    newField.SetWidth(fieldwidth[j])
    newField.SetPrecision(fieldprecision[j])
    dst_layer.CreateField(newField)                                               

  layer_defn = dst_layer.GetLayerDefn()

  count = 0
  pointsX = []; pointsY = []
  for feat in lyr:
    geom = feat.GetGeometryRef()
    xc = geom.GetX()
    yc = geom.GetY()
    xcout, ycout = pseudomerc(xc, yc)
    newpnts = np.asarray([xcout, ycout]) + circpnts
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for j in range(circpnts.shape[0]):
      ring.AddPoint(newpnts[j,0], newpnts[j,1])
    ring.CloseRings()
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    outfeat = ogr.Feature(layer_defn)
    outfeat.SetGeometry(poly)
    outfeat.SetFID(count)
    for j in range(0, fieldcnt):
      fdata = feat.GetField(j)
      outfeat.SetField(fieldname[j], fdata)
    dst_layer.CreateFeature(outfeat)
    count += 1

  ## close the input and output shapefiles
  vecDS.Destroy()
  dstDS.Destroy()


if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ USAGE ] you must supply 2 arguments: make_gedi_shot_circles.py inshape outshape")
    print("")
    sys.exit( 1 )

  main( sys.argv[1], sys.argv[2] )

