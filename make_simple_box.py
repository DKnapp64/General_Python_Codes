path='wkop_vswir_box.shp'
import osgeo.ogr, osgeo.osr #we will need some packages
from osgeo import ogr #and one more for the creation of a new field
#will create a spatial reference locally to tell the system what the reference will be
spatialReference = osgeo.osr.SpatialReference()

#here we define this reference to be utm Zone 18 South with wgs84...
spatialReference.ImportFromProj4('+proj=utm +zone=5 +ellps=WGS84 +datum=WGS84 +units=m') 

driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
shapeData = driver.CreateDataSource(path)
layer = shapeData.CreateLayer('testit', spatialReference, osgeo.ogr.wkbPolygon)
layer_defn = layer.GetLayerDefn() # gets parameters of the current shapefile
fieldDefn = ogr.FieldDefn('polyid', ogr.OFTInteger)
layer.CreateField(fieldDefn)

ring = osgeo.ogr.Geometry(osgeo.ogr.wkbLinearRing)

ring.AddPoint(270054.00, 2163958.00)
ring.AddPoint(300788.00, 2163958.00)
ring.AddPoint(300788.00, 2137044.00)
ring.AddPoint(270054.00, 2137044.00)
ring.CloseRings()

poly = osgeo.ogr.Geometry(osgeo.ogr.wkbPolygon)
poly.AddGeometry(ring)
featureIndex = 0 #this will be the second polygon in our dataset
##now lets write this into our layer/shape file:
feature = osgeo.ogr.Feature(layer_defn)
feature.SetGeometry(poly)
feature.SetFID(featureIndex)
feature.SetField('polyid', 0)
layer.CreateFeature(feature)

poly = None
feature = None
shapeData.Destroy() #lets close the shapefile

# shapeData = ogr.Open(path, 1)
# layer = shapeData.GetLayer() #get possible layers.
# layer_defn = layer.GetLayerDefn() #get definitions of the layer
