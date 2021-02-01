#!/bin/env python3
import ogr, osr
import numpy as np
import json
import rasterio as rio
import mosaic_quads
import os, sys

MOSAIC_LEVEL = 15
MOSAIC_TILE_SIZE = 4096
WEBM_EARTH_RADIUS = 6378137.0
WEBM_ORIGIN = -np.pi * WEBM_EARTH_RADIUS

infile = 'vs_polygons_webmerc.gpkg'
outfile = 'global_quads_coral_20200621.shp'
vDS = ogr.GetDriverByName('GPKG').Open(infile, 0)
lyr = vDS.GetLayer('vs_polygons')
width = MOSAIC_TILE_SIZE * 2 * abs(WEBM_ORIGIN) / (2**MOSAIC_LEVEL * 256)
psize = width/4096
num_tiles = int(2.0**MOSAIC_LEVEL * 256 / MOSAIC_TILE_SIZE)
transform = rio.transform.from_origin(WEBM_ORIGIN, -WEBM_ORIGIN, width, width)

drv = ogr.GetDriverByName('ESRI Shapefile')
spref = osr.SpatialReference()
spref.ImportFromEPSG(3857)   ## Web Mercator projection

outDS = drv.CreateDataSource(outfile)
outlyr = outDS.CreateLayer('quad_polygons', spref, ogr.wkbPolygon)
nameFieldDefn = ogr.FieldDefn("QUADNAME", ogr.OFTString)
noaaareaFieldDefn = ogr.FieldDefn("NOAANAME", ogr.OFTString)
nameFieldDefn.SetWidth(16)
noaaareaFieldDefn.SetWidth(45)
outlyr.CreateField(nameFieldDefn)
outlyr.CreateField(noaaareaFieldDefn)
outlyrDefn = outlyr.GetLayerDefn()
##  rio.transform.xy(transform, 0, 1, offset='ul')

for i in range(0, 213*2, 2):
  feat = lyr.GetFeature(i+2)
  featjsonstr = feat.ExportToJson()
  featjson = json.loads(featjsonstr)
  noaaname = featjson['properties']['name']
  quadlist = mosaic_quads.determine_mosaic_quads_for_geometry(featjson['geometry'])
  for thisquad in quadlist:
    gride = int(thisquad[4:8])
    gridn = int(thisquad[10:14])
    ulx,uly = rio.transform.xy(transform, gridn, gride, offset='ul')
    urx,ury = rio.transform.xy(transform, gridn, gride, offset='ur')
    lrx,lry = rio.transform.xy(transform, gridn, gride, offset='lr')
    llx,lly = rio.transform.xy(transform, gridn, gride, offset='ll')
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(ulx, -uly)
    ring.AddPoint(urx, -ury)
    ring.AddPoint(lrx, -lry)
    ring.AddPoint(llx, -lly)
    ring.AddPoint(ulx, -uly)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    newfeat = ogr.Feature(outlyrDefn)
    newfeat.SetGeometry(poly)
    newfeat.SetField("QUADNAME", thisquad)
    newfeat.SetField("NOAANAME", noaaname)
    outlyr.CreateFeature(newfeat)
    newfeat = None
  print('Finished %d quads for number %d: %s' % (len(quadlist), (i+2)//2, noaaname))

vDS, outDS = None, None
