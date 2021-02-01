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

## SOURCESHP: String (254.0)
## SOURCEFID: Integer (9.0)
## BEAM: Integer64 (18.0)
## SHOT_NUMBE: Integer64 (18.0)
## ELEV_HIGH: Real (24.15)
## ELEV_LOW: Real (24.15)
## HEIGHT: Real (24.15)
## ELEV_LAST: Real (24.15)
## ELEV_LAST_: Real (24.15)
## ELEV_BIN0: Real (24.15)
## ELEV_BIN0_: Real (24.15)
## HEIGHT2: Real (24.15)
## HGT_BIN0: Real (24.15)
## HGT_LASTBI: Real (24.15)
## HEIGHT3: Real (24.15)
## COVER: Real (24.15)
## PAI: Real (24.15)
## PGAP_THETA: Real (24.15)
## PGAP_THE_1: Real (24.15)
## RH100: Integer64 (18.0)
## LSTREECOV: Real (24.15)
## MODTREECOV: Real (24.15)
## L2A_QUAL: Integer64 (18.0)
## L2B_QUAL: Integer64 (18.0)
## DEGRADE: Integer64 (18.0)
## SENSI: Real (24.15)
## SOLARELEV: Real (24.15)
## ALGORUN: Integer64 (18.0)

  for j in range(fieldcnt):
    fieldname.append(lyrdefn.GetFieldDefn(j).GetName())
    fieldtypecode.append(lyrdefn.GetFieldDefn(j).GetType())
    fieldtype.append(ogr.GetFieldTypeName(fieldtypecode[j]))
    fieldwidth.append(lyrdefn.GetFieldDefn(j).GetWidth())
    fieldprecision.append(lyrdefn.GetFieldDefn(j).GetPrecision())
    print(fieldname[j], fieldtypecode[j], fieldtype[j], fieldwidth[j], fieldprecision[j])

  fieldtypecode[2] = 0
  fieldtype[2] = 'Integer'
  fieldwidth[2] = 9
  fieldprecision[2] = 0
  fieldtypecode[4] = 2
  fieldtype[4] = 'Real'
  fieldwidth[4] = 9
  fieldprecision[4] = 2
  fieldtypecode[5] = 2
  fieldtype[5] = 'Real'
  fieldwidth[5] = 9
  fieldprecision[5] = 2
  fieldtypecode[6] = 2
  fieldtype[6] = 'Real'
  fieldwidth[6] = 9
  fieldprecision[6] = 2
  fieldtypecode[7] = 2
  fieldtype[7] = 'Real'
  fieldwidth[7] = 9
  fieldprecision[7] = 3
  fieldtypecode[8] = 2
  fieldtype[8] = 'Real'
  fieldwidth[8] = 9
  fieldprecision[8] = 3
  fieldtypecode[9] = 2
  fieldtype[9] = 'Real'
  fieldwidth[9] = 9
  fieldprecision[9] = 2
  fieldtypecode[10] = 2
  fieldtype[10] = 'Real'
  fieldwidth[10] = 9
  fieldprecision[10] = 2
  fieldtypecode[11] = 0
  fieldtype[11] = 'Integer'
  fieldwidth[11] = 3
  fieldprecision[11] = 0
  fieldtypecode[12] = 0
  fieldtype[12] = 'Integer'
  fieldwidth[12] = 3
  fieldprecision[12] = 0
  fieldtypecode[13] = 0
  fieldtype[13] = 'Integer'
  fieldwidth[13] = 3
  fieldprecision[13] = 0
  fieldtypecode[14] = 2
  fieldtype[14] = 'Real'
  fieldwidth[14] = 9
  fieldprecision[14] = 6
  fieldtypecode[15] = 2
  fieldtype[15] = 'Real'
  fieldwidth[15] = 12
  fieldprecision[15] = 8
  fieldtypecode[16] = 2
  fieldtype[16] = 'Integer'
  fieldwidth[16] = 3
  fieldprecision[16] = 0

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
    for j in range(fieldcnt):
      fdata = feat.GetField(j)
      outfeat.SetField(fieldname[j], fdata)
    dst_layer.CreateFeature(outfeat)
    count += 1

  ## close the input and output shapefiles
  vecDS.Destroy()
  dstDS.Destroy()


if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ USAGE ] you must supply 2 arguments: make_gedi_shot_footprints.py inpattern outshape")
    print("")
    sys.exit( 1 )

  main( sys.argv[1], sys.argv[2] )

