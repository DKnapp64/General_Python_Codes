import ogr
import osr
import numpy as np
import csv

## csvfile = 'Database_15082016_from_Becca.csv'
## outfile = 'database_15082016_from_becca.shp'
csvfile = 'shawna_locations.csv'
outfile = 'shawna_15m_pont_centers_latlon.shp'

#Set up blank lists for data
site, region, island, latitude, longitude = [],[],[],[],[]

#read data from csv file and store in lists
## with open('/caofs/scratch/dave/dogs/den_random_points_20150723.csv', 'rb') as csvfile:
with open(csvfile, 'r') as f:
  r = csv.reader(f, delimiter=',')
  for row in r:
    if (row[0] == 'SITE'):
      continue
    site.append(row[0])
    region.append(row[1])
    island.append(row[2])
    latitude.append(float(row[3]))
    longitude.append(float(row[4]))

spatialReference = osr.SpatialReference()
spatialReference.ImportFromEPSG(4326) 

driver = ogr.GetDriverByName('ESRI Shapefile')
shapeData = driver.CreateDataSource(outfile)
layer = shapeData.CreateLayer('centers', spatialReference, ogr.wkbPoint)
layer_defn = layer.GetLayerDefn() # gets parameters of the current shapefile
SiteDefn = ogr.FieldDefn('Site', ogr.OFTString)
layer.CreateField(SiteDefn)
RegionDefn = ogr.FieldDefn('Region', ogr.OFTString)
layer.CreateField(RegionDefn)
IslandDefn = ogr.FieldDefn('Island', ogr.OFTString)
layer.CreateField(IslandDefn)
LatDefn = ogr.FieldDefn('Latitude', ogr.OFTReal)
layer.CreateField(LatDefn)
LonDefn = ogr.FieldDefn('Longitude', ogr.OFTReal)
layer.CreateField(LonDefn)

featureIndex = 0

for j in range(0,len(site)):
  
  thislat = latitude[j]
  thislon = longitude[j]
  thissite = site[j]
  thisregion = region[j]
  thisisland = island[j]

  pnt = ogr.Geometry(ogr.wkbPoint)

  pnt.AddPoint(thislon, thislat)

  ##now lets write this into our layer/shape file:
  feature = ogr.Feature(layer_defn)
  feature.SetGeometry(pnt)
  feature.SetFID(featureIndex)
  feature.SetField('Site', thissite)
  feature.SetField('Region', thisregion)
  feature.SetField('Island', thisisland)
  feature.SetField('Latitude', thislat)
  feature.SetField('Longitude', thislon)
  layer.CreateFeature(feature)
  featureIndex += 1

shapeData.Destroy() #lets close the shapefile
