#!/bin/env python3
import gdal, ogr, osr
import numpy as np
from datetime import date, datetime
import pandas as pd

## infile = "Final_data_2019_transects.csv"
## infile = 'transect_bigisland_25m.csv'
## Site, Date, Transect ,Depth (m),Live Coral,Dead\Algal ,Sand ,CCA,Bleach ,Other ,Lat Start ,Long Start ,Lat End ,Long End ,Compas heading (degrees),XStart,YStart,XStop,YStop,,,,,,,,
## Papabay,1,15,50,47,0,3,0,0,N 19 12.5951,W 155 54.0910,N 19 12.5895,W 155 54.1035,230,-155.9015167,19.20991833,-155.901725,19.209825,,,,,,,,

infile = "Final_data_2019_transects_kaneohe_adj.csv"
## Site,Transect ,Depth (m),Live Coral,Dead\Algal ,Sand ,CCA,Paling,Bleach ,Other ,Lat Start ,Long Start ,Lat End ,Long End ,Compas heading (degrees),YStart,XStart,YStop,XStop

str2date = lambda x: datetime.strptime(x, '%m/%d/%Y')

df = pd.read_csv(infile, skipinitialspace=True, infer_datetime_format=True)

path='transect_otherislands_25m.shp'

spatialReference = osr.SpatialReference()
spatialReference.ImportFromEPSG(4326) 

driver = ogr.GetDriverByName('ESRI Shapefile')
shapeData = driver.CreateDataSource(path)
layer = shapeData.CreateLayer('transects', spatialReference, ogr.wkbLineString)
layer_defn = layer.GetLayerDefn() # gets parameters of the current shapefile
SiteDefn = ogr.FieldDefn('Site', ogr.OFTString)
layer.CreateField(SiteDefn)
DateDefn = ogr.FieldDefn('Date', ogr.OFTString)
layer.CreateField(DateDefn)
TransDefn = ogr.FieldDefn('Transect', ogr.OFTString)
layer.CreateField(TransDefn)
DepthDefn = ogr.FieldDefn('Depth', ogr.OFTReal)
DepthDefn.SetWidth(5)
DepthDefn.SetPrecision(2)
layer.CreateField(DepthDefn)
LiveDefn = ogr.FieldDefn('LiveCoral', ogr.OFTReal)
LiveDefn.SetWidth(5)
LiveDefn.SetPrecision(1)
layer.CreateField(LiveDefn)
DeadDefn = ogr.FieldDefn('DeadAlgal', ogr.OFTReal)
DeadDefn.SetWidth(5)
DeadDefn.SetPrecision(1)
layer.CreateField(DeadDefn)
SandDefn = ogr.FieldDefn('Sand', ogr.OFTReal)
SandDefn.SetWidth(5)
SandDefn.SetPrecision(1)
layer.CreateField(SandDefn)
CCADefn = ogr.FieldDefn('CCA', ogr.OFTReal)
CCADefn.SetWidth(5)
CCADefn.SetPrecision(1)
layer.CreateField(CCADefn)
PaleDefn = ogr.FieldDefn('Paling', ogr.OFTReal)
PaleDefn.SetWidth(5)
PaleDefn.SetPrecision(1)
layer.CreateField(PaleDefn)
BleachDefn = ogr.FieldDefn('Bleach', ogr.OFTReal)
BleachDefn.SetWidth(5)
BleachDefn.SetPrecision(1)
layer.CreateField(BleachDefn)
OtherDefn = ogr.FieldDefn('Other', ogr.OFTReal)
OtherDefn.SetWidth(5)
OtherDefn.SetPrecision(1)
layer.CreateField(OtherDefn)
PercBleachDefn = ogr.FieldDefn('PercBleach', ogr.OFTReal)
PercBleachDefn.SetWidth(5)
PercBleachDefn.SetPrecision(1)
layer.CreateField(PercBleachDefn)
CompassDefn = ogr.FieldDefn('Compass', ogr.OFTReal)
CompassDefn.SetWidth(5)
CompassDefn.SetPrecision(0)
layer.CreateField(CompassDefn)

featureIndex = 0

for i,thisLine in df.iterrows():
  
  startlat = thisLine['YStart']
  startlon = thisLine['XStart']
  endlat = thisLine['YStop']
  endlon = thisLine['XStop']

  line = ogr.Geometry(ogr.wkbLineString)

  line.AddPoint_2D(startlon, startlat)
  line.AddPoint_2D(endlon, endlat)

  ##now lets write this into our layer/shape file:
  feature = ogr.Feature(layer_defn)
  feature.SetGeometry(line)
  feature.SetFID(featureIndex)
  feature.SetField('Site', str(thisLine[0]))
  feature.SetField('Date', str(thisLine[1]))
  feature.SetField('Transect', int(thisLine[2]))
  feature.SetField('Depth', float(thisLine[3]))
  feature.SetField('LiveCoral', float(thisLine[4]))
  feature.SetField('DeadAlgal', float(thisLine[5]))
  feature.SetField('Sand', float(thisLine[6]))
  feature.SetField('CCA', float(thisLine[7]))
  feature.SetField('Paling', float(thisLine[8]))
  feature.SetField('Bleach', float(thisLine[9]))
  feature.SetField('Other', float(thisLine[10]))
  feature.SetField('PercBleach', 100 * float(thisLine[9])/(float(thisLine[9]) + float(thisLine[4])))
  feature.SetField('Compass', float(thisLine[14]))
  layer.CreateFeature(feature)
  featureIndex += 1

shapeData.Destroy() #lets close the shapefile
