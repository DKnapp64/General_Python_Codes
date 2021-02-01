import gdal, ogr, osr
import numpy as np

infile = "Final_data_2019_transects.csv"
## Site,Transect ,Depth (m),Live Coral,Dead\Algal ,Sand ,CCA,Bleach ,Other ,Lat Start ,Long Start ,Lat End ,Long End ,Compas heading (degrees),XStart,YStart,XStop,YStop,,,,,,,,
## Papabay,1,15,50,47,0,3,0,0,N 19 12.5951,W 155 54.0910,N 19 12.5895,W 155 54.1035,230,-155.9015167,19.20991833,-155.901725,19.209825,,,,,,,,
data = np.genfromtxt(infile, delimiter=',', names=True,
  dtype=[('SiteName', 'S15'), ('TransectID', 'i8'),
  ('Depth', 'f8'), ('LiveCoral', 'i8'), ('DeadAlgal', 'i8'),
  ('Sand', 'i8'), ('CCA', 'i8'), ('Bleach', 'i8'),
  ('Other', 'i8'), ('StartLat', 'S12'), ('StartLon', 'S12'),
  ('EndLat', 'S12'), ('EndLon', 'S12'), ('Compass', 'i8'),
  ('XStart', 'f8'), ('YStart', 'f8'),
  ('XStop', 'f8'), ('YStop', 'f8')])

path='Final_data_2019_transects.shp'

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
BleachDefn = ogr.FieldDefn('Bleach', ogr.OFTReal)
layer.CreateField(BleachDefn)
OtherDefn = ogr.FieldDefn('Other', ogr.OFTReal)
layer.CreateField(OtherDefn)

featureIndex = 0

for thisLine in data:
  
  startlat = thisLine[15]
  startlon = thisLine[14]
  endlat = thisLine[17]
  endlon = thisLine[16]

  line = ogr.Geometry(ogr.wkbLineString)

  line.AddPoint_2D(startlon, startlat)
  line.AddPoint_2D(endlon, endlat)

  ##now lets write this into our layer/shape file:
  feature = ogr.Feature(layer_defn)
  feature.SetGeometry(line)
  feature.SetFID(featureIndex)
  feature.SetField('TransName', str(thisLine[0].decode()))
  feature.SetField('TransID', int(thisLine[1]))
  feature.SetField('Depth', float(thisLine[2]))
  feature.SetField('LiveCoral', float(thisLine[3]))
  feature.SetField('DeadAlgal', float(thisLine[4]))
  feature.SetField('Sand', float(thisLine[5]))
  feature.SetField('CCA', float(thisLine[6]))
  feature.SetField('Bleach', float(thisLine[7]))
  feature.SetField('Other', float(thisLine[8]))
  layer.CreateFeature(feature)
  featureIndex += 1

shapeData.Destroy() #lets close the shapefile
