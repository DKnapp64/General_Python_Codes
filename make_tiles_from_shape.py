#!/bin/env python3
import sys
import os, math
import gdal, ogr, osr
import numpy as np

def main( inshape, outtileshp ):

  drv = ogr.GetDriverByName('ESRI Shapefile')
  siteshp = drv.Open(inshape, 0)
  lyr = siteshp.GetLayer(0)
  sourceSR = lyr.GetSpatialRef()
  defn = lyr.GetLayerDefn()
  feat = lyr.GetNextFeature()
  geom = feat.GetGeometryRef()
  minbb = geom.GetEnvelope()
 
  startx = math.floor(minbb[0]/600.0) * 600.0
  endx = math.ceil(minbb[1]/600.0) * 600.0
  starty = math.floor(minbb[2]/600.0) * 600.0
  endy = math.ceil(minbb[3]/600.0) * 600.0

  numcols = int((endx-startx)/600.0)
  numrows = int((endy-starty)/600.0)

  tileData = drv.CreateDataSource(outtileshp)
  layer = tileData.CreateLayer('tiles', sourceSR, ogr.wkbPolygon)
  layer_defn = layer.GetLayerDefn() # gets parameters of the current shapefile
  siteDefn = ogr.FieldDefn('SiteName', ogr.OFTString)
  layer.CreateField(siteDefn)
  tileidDefn = ogr.FieldDefn('Tile', ogr.OFTInteger)
  layer.CreateField(tileidDefn)

  featIndex = 0

  for k in np.arange(numrows):
    for j in np.arange(numcols):
      myx = startx + (j*600.0)
      myy = endy - (k*600.0)
      ring = ogr.Geometry(ogr.wkbLinearRing)
      ring.AddPoint(myx, myy)
      ring.AddPoint(myx+600.0, myy)
      ring.AddPoint(myx+600.0, myy-600.0)
      ring.AddPoint(myx, myy-600.0)
      ring.CloseRings()
      poly = ogr.Geometry(ogr.wkbPolygon)
      poly.AddGeometry(ring)
      if (geom.Intersects(poly)):
        featIndex += 1 
        feature = ogr.Feature(layer_defn)
        feature.SetGeometry(poly)
        feature.SetFID(featIndex-1)
        feature.SetField('SiteName', inshape)
        feature.SetField('Tile', featIndex)
        layer.CreateFeature(feature)
      else:
        continue

  poly = None
  feature = None
  tileData.Destroy() #lets close the shapefile
  siteshp.Destroy() #lets close the shapefile

if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ ERROR ] you must supply 2 arguments: make_tiles_from_shape.py siteshape tileshape")
    print("where:")
    print("         siteshape = the shape file with the site outline.")
    print("         tileshape = the output shape file with the tile polygons.")
    print("")

    sys.exit( 1 )

  main( sys.argv[1], sys.argv[2] )
