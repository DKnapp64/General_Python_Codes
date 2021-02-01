#!/bin/env python3
import gdal, ogr, osr
import numpy as np

infile = "kaneohe_post_dive_20191014.csv"

data = np.genfromtxt(infile, delimiter=',', skip_header=1,
  dtype=[('SiteName', 'U35'), ('TransectID', 'i8'),
  ('Depth', 'f8'), ('LiveCoral', 'i8'), ('DeadAlgal', 'i8'),
  ('Sand', 'i8'), ('CCA', 'i8'), ('Paling', 'i8'), ('Bleach', 'i8'),
  ('Other', 'i8'), ('StartLat', 'U12'), ('StartLon', 'U12'),
  ('EndLat', 'U12'), ('EndLon', 'U12'), ('Compass', 'i8')])

path='kaneohe_post_dove_20191014.shp'

spatialReference = osr.SpatialReference()
spatialReference.ImportFromEPSG(4326) 

driver = ogr.GetDriverByName('ESRI Shapefile')
shapeData = driver.CreateDataSource(path)
layer = shapeData.CreateLayer('transects', spatialReference, ogr.wkbLineString)
layer_defn = layer.GetLayerDefn() # gets parameters of the current shapefile
TransDefn = ogr.FieldDefn('TransName', ogr.OFTString)
layer.CreateField(TransDefn)
TransIDDefn = ogr.FieldDefn('TransID', ogr.OFTInteger)
layer.CreateField(TransIDDefn)
DepthDefn = ogr.FieldDefn('Depth', ogr.OFTReal)
layer.CreateField(DepthDefn)
LiveDefn = ogr.FieldDefn('LiveCoral', ogr.OFTReal)
layer.CreateField(LiveDefn)
DeadDefn = ogr.FieldDefn('DeadAlgal', ogr.OFTReal)
layer.CreateField(DeadDefn)
SandDefn = ogr.FieldDefn('Sand', ogr.OFTReal)
layer.CreateField(SandDefn)
CCADefn = ogr.FieldDefn('CCA', ogr.OFTReal)
layer.CreateField(CCADefn)
PaleDefn = ogr.FieldDefn('Paling', ogr.OFTReal)
layer.CreateField(PaleDefn)
BleachDefn = ogr.FieldDefn('Bleach', ogr.OFTReal)
layer.CreateField(BleachDefn)
OtherDefn = ogr.FieldDefn('Other', ogr.OFTReal)
layer.CreateField(OtherDefn)
CompassDefn = ogr.FieldDefn('Compass', ogr.OFTInteger)
layer.CreateField(CompassDefn)

featureIndex = 0

for thisLine in data:
  startlat = float(thisLine[10].split()[1])
  if (thisLine[10].split()[0] == 'S'):
    startlat *= -1 
  startlon = float(thisLine[11].split()[1])
  if (thisLine[11].split()[0] == 'W'):
    startlon *= -1 
  endlat = float(thisLine[12].split()[1])
  if (thisLine[12].split()[0] == 'S'):
    endlat *= -1 
  endlon = float(thisLine[13].split()[1])
  if (thisLine[13].split()[0] == 'W'):
    endlon *= -1 

  line = ogr.Geometry(ogr.wkbLineString)

  line.AddPoint_2D(startlon, startlat)
  line.AddPoint_2D(endlon, endlat)

  ##now lets write this into our layer/shape file:
  feature = ogr.Feature(layer_defn)
  feature.SetGeometry(line)
  feature.SetFID(featureIndex)
  feature.SetField('TransName', str(thisLine[0]))
  feature.SetField('TransID', int(thisLine[1]))
  feature.SetField('Depth', float(thisLine[2]))
  feature.SetField('LiveCoral', float(thisLine[3]))
  feature.SetField('DeadAlgal', float(thisLine[4]))
  feature.SetField('Sand', float(thisLine[5]))
  feature.SetField('CCA', float(thisLine[6]))
  feature.SetField('Paling', float(thisLine[7]))
  feature.SetField('Bleach', float(thisLine[8]))
  feature.SetField('Other', float(thisLine[9]))
  feature.SetField('Compass', float(thisLine[14]))
  layer.CreateFeature(feature)
  featureIndex += 1

shapeData.Destroy() #lets close the shapefile
