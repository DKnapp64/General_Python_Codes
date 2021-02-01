#!/bin/env python3
import gdal, ogr, osr
import numpy as np
import pandas as pd

infile = "20191127_hotspot_video_validation.csv"
str2date = lambda x: datetime.strptime(x, '%m/%d/%Y')
df = pd.read_csv(infile, skipinitialspace=True, infer_datetime_format=True)

path='hotspots_points_20191202.shp'

spatialReference = osr.SpatialReference()
spatialReference.ImportFromEPSG(4326) 
## ID#,Date,x,y,Island,Mean Unbleached ,Mean Bleached,Mean Percentage Bleached,Notes

driver = ogr.GetDriverByName('ESRI Shapefile')
shapeData = driver.CreateDataSource(path)
layer = shapeData.CreateLayer('hotspots', spatialReference, ogr.wkbPoint)
layer_defn = layer.GetLayerDefn() # gets parameters of the current shapefile
IDDefn = ogr.FieldDefn('ID', ogr.OFTString)
layer.CreateField(IDDefn)
DateDefn = ogr.FieldDefn('Date', ogr.OFTString)
layer.CreateField(DateDefn)
IslandDefn = ogr.FieldDefn('Island', ogr.OFTString)
layer.CreateField(IslandDefn)
MUnBlDefn = ogr.FieldDefn('MeanUnBl', ogr.OFTReal)
MUnBlDefn.SetWidth(5)
MUnBlDefn.SetPrecision(1)
layer.CreateField(MUnBlDefn)
MBlDefn = ogr.FieldDefn('MeanBl', ogr.OFTReal)
MBlDefn.SetWidth(5)
MBlDefn.SetPrecision(1)
layer.CreateField(MBlDefn)
MeanPerBlDefn = ogr.FieldDefn('MeanPerBl', ogr.OFTReal)
MeanPerBlDefn.SetWidth(5)
MeanPerBlDefn.SetPrecision(1)
layer.CreateField(MeanPerBlDefn)
NotesDefn = ogr.FieldDefn('Notes', ogr.OFTString)
layer.CreateField(NotesDefn)

featureIndex = 0

for k,recs in df.iterrows():
  lat = recs['x']
  lon = recs['y']

  pnt = ogr.Geometry(ogr.wkbPoint)

  pnt.AddPoint(lon, lat)

  ##now lets write this into our layer/shape file:
  feature = ogr.Feature(layer_defn)
  feature.SetGeometry(pnt)
  feature.SetFID(featureIndex)
  feature.SetField('ID', str(recs['ID#']))
  feature.SetField('Date', str(recs['Date']))
  feature.SetField('Island', str(recs['Island']))
  feature.SetField('MeanUnBl', recs['Mean Unbleached '])
  feature.SetField('MeanBl', recs['Mean Bleached'])
  feature.SetField('MeanPerBl', recs['Mean Percentage Bleached'])
  feature.SetField('Notes', recs['Notes'])
  layer.CreateFeature(feature)
  featureIndex += 1

shapeData.Destroy() #lets close the shapefile
