import gdal, ogr, osr
import numpy as np
import pdb

infile = "fieldwork_visits.csv"
data = np.genfromtxt("field_work_visits.csv", delimiter=',', names=True, \
  dtype=[('SiteID', 'i8'), ('SiteName', 'S15'), ('StartLat', 'S12'), ('StartLon', 'S12'), \
  ('EndLat', 'S12'), ('EndLon', 'S12'), ('ChangeTotBiomass', 'f8'), ('ChangeHerbBiomass', 'f8')])

path='field_works_visits.shp'

import ogr, osr #we will need some packages
## spatialReference.ImportFromProj4('+proj=utm +zone=5 +ellps=WGS84 +datum=WGS84 +units=m') 
spatialReference = osr.SpatialReference()
spatialReference.ImportFromEPSG(4326) 


driver = ogr.GetDriverByName('ESRI Shapefile')
shapeData = driver.CreateDataSource(path)
layer = shapeData.CreateLayer('field_works_visits', spatialReference, ogr.wkbLineString)
layer_defn = layer.GetLayerDefn() # gets parameters of the current shapefile
siteDefn = ogr.FieldDefn('SiteName', ogr.OFTString)
layer.CreateField(siteDefn)
siteidDefn = ogr.FieldDefn('SiteId', ogr.OFTInteger)
layer.CreateField(siteidDefn)
ctbDefn = ogr.FieldDefn('ChangeB', ogr.OFTReal)
layer.CreateField(ctbDefn)
chbDefn = ogr.FieldDefn('ChangeH', ogr.OFTReal)
layer.CreateField(chbDefn)

featureIndex = 0

for thisLine in data:
  
  templat = thisLine[2].split()
  if (chr(templat[0][0]) == 'N'):
    startlat = float(templat[0][1:]) + (float(templat[1])/60.)
  else:
    startlat = -(float(templat[0][1:]) + (float(templat[1])/60.))
  templon = thisLine[3].split()
  if (chr(templon[0][0]) == 'E'):
    startlon = float(templon[0][1:]) + (float(templon[1])/60.)
  else:
    startlon = -(float(templon[0][1:]) + (float(templon[1])/60.))

  templat = thisLine[4].split()
  if (chr(templat[0][0]) == 'N'):
    endlat = float(templat[0][1:]) + (float(templat[1])/60.)
  else:
    endlat = -(float(templat[0][1:]) + (float(templat[1])/60.))
  templon = thisLine[5].split()
  if (chr(templon[0][0]) == 'E'):
    endlon = float(templon[0][1:]) + (float(templon[1])/60.)
  else:
    endlon = -(float(templon[0][1:]) + (float(templon[1])/60.))

  pdb.set_trace()

  line = ogr.Geometry(ogr.wkbLineString)

  line.AddPoint_2D(startlon, startlat)
  line.AddPoint_2D(endlon, endlat)

  ##now lets write this into our layer/shape file:
  feature = ogr.Feature(layer_defn)
  feature.SetGeometry(line)
  feature.SetFID(featureIndex)
  feature.SetField('SiteName', str(thisLine[1]))
  feature.SetField('SiteId', int(thisLine[0]))
  feature.SetField('ChangeB', float(thisLine[6]))
  feature.SetField('ChangeH', float(thisLine[7]))
  layer.CreateFeature(feature)

  featureIndex += 1

shapeData.Destroy() #lets close the shapefile

# shapeData = ogr.Open(path, 1)
# layer = shapeData.GetLayer() #get possible layers.
# layer_defn = layer.GetLayerDefn() #get definitions of the layer
