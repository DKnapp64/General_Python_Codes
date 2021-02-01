#!/usr/bin/python
import gdal, ogr, osr, numpy
import sys
import csv


def zonal_stats(feat, input_zone_polygon, input_value_raster):

    # Open data
    raster = gdal.Open(input_value_raster)
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()
    ## for anp_nacional*
    ## featval = feat.GetField("OBJECTID")
    featname = feat.GetField("ANP_NOMB")
    featcategory = feat.GetField("ANP_CATE")
    ## FOR anp_privada* and anp_region*
    ## featval = feat.GetField("OBJECTID")
    ## featname = feat.GetField("ANPC_NOMB")
    ## featcategory = feat.GetField("ANPC_CAT")
    ## FOR ECOTOURISM
    ## featval = feat.GetField("Num")
    ## featname = feat.GetField("BENEFIC")
    ## featcategory = feat.GetField("TITULAR")
    ## FOR REFORESTATION
    ## featname = feat.GetField("BENEFIC")
    ## featcategory = feat.GetField("TITULAR")
    ## FOR mfauna
    ## featname = feat.GetField("BENEFICIAR")
    ## featcategory = feat.GetField("TITULAR")
    ## FOR CASTANA (Brazil Nut)
    ## featname = feat.GetField("BENEFIC")
    ## featcategory = feat.GetField("NOMB_APELL")
    ## FOR SHIRINGA (Rubber)
    ## featname = feat.GetField("NOMBRE")
    ## featcategory = feat.GetField("TITULAR")
    ## FOR CONSERVATION
    ## featname = feat.GetField("BENEFIC")
    ## featcategory = feat.GetField("TITULAR")

    # Get raster georeference info
    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    # Reproject vector geometry to same projection as raster
    sourceSR = lyr.GetSpatialRef()
    targetSR = osr.SpatialReference()
    targetSR.ImportFromWkt(raster.GetProjectionRef())
    coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
    ## feat = lyr.GetNextFeature()
    geom = feat.GetGeometryRef()
    geom.Transform(coordTrans)

    # Get extent of feature
    geom = feat.GetGeometryRef()
    if (geom.GetGeometryName() == 'MULTIPOLYGON'):
        count = 0
        pointsX = []; pointsY = []
        for polygon in geom:
            geomInner = geom.GetGeometryRef(count)
            ring = geomInner.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            for p in range(numpoints):
                    lon, lat, z = ring.GetPoint(p)
                    pointsX.append(lon)
                    pointsY.append(lat)
            count += 1
    elif (geom.GetGeometryName() == 'POLYGON'):
        ring = geom.GetGeometryRef(0)
        numpoints = ring.GetPointCount()
        pointsX = []; pointsY = []
        for p in range(numpoints):
                lon, lat, z = ring.GetPoint(p)
                pointsX.append(lon)
                pointsY.append(lat)

    else:
        sys.exit("ERROR: Geometry needs to be either Polygon or Multipolygon")

    xmin = min(pointsX)
    xmax = max(pointsX)
    ymin = min(pointsY)
    ymax = max(pointsY)

    # Specify offset and rows and columns to read
    xoff = int((xmin - xOrigin)/pixelWidth)
    yoff = int((yOrigin - ymax)/pixelWidth)
    xcount = int((xmax - xmin)/pixelWidth)+1
    ycount = int((ymax - ymin)/pixelWidth)+1

    # Create memory target raster
    target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
        xmin, pixelWidth, 0,
        ymax, 0, pixelHeight,
    ))

    # Create for target raster the same projection as for the value raster
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjectionRef())
    target_ds.SetProjection(raster_srs.ExportToWkt())

    # Rasterize zone polygon to raster
    ## gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])
    ## lyr.SetAttributeFilter(" OBJECTID = 2 ")
    gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

    # Read raster as arrays
    banddataraster = raster.GetRasterBand(1)
    dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)

    bandmask = target_ds.GetRasterBand(1)

    ## if (featval == 4):
    ##   testout = gdal.GetDriverByName('GTiff').Create('testout4.tif', xcount, ycount, 1, gdal.GDT_Byte)
    ##   testout.SetGeoTransform((xmin, pixelWidth, 0, ymax, 0, pixelHeight,))
    ##   testout.SetProjection(raster_srs.ExportToWkt())
    ##   testout.GetRasterBand(1).WriteArray(bandmask.ReadAsArray(0,0,xcount, ycount).astype(numpy.byte))
    
    datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)

    # Mask zone of raster
    ## pdb.set_trace()
    zoneraster = numpy.ma.masked_array(dataraster,  numpy.logical_not(datamask))
    ## pdb.set_trace()
    if (numpy.ma.sum(zoneraster) == 0):
      zoneraster2 = zoneraster
    else:
      # zoneraster2 = numpy.ma.masked_values(zoneraster, 0)
      zoneraster2 = numpy.ma.masked_less_equal(zoneraster, 0)

    # Calculate statistics of zonal raster
    return featname, featcategory, numpy.ma.mean(zoneraster2),numpy.asscalar((numpy.ma.median(zoneraster2)).data),numpy.ma.std(zoneraster2),numpy.asscalar(numpy.ma.minimum(zoneraster2).data), numpy.asscalar(numpy.ma.maximum(zoneraster2).data), numpy.count_nonzero(datamask)


def loop_zonal_stats(input_zone_polygon, input_value_raster):

    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()
    featList = range(lyr.GetFeatureCount())
    statDict = {}

    for FID in featList:
        feat = lyr.GetFeature(FID)
        meanValue = zonal_stats(feat, input_zone_polygon, input_value_raster)
        statDict[FID] = meanValue

    with open('peru_protected_areas_elev_national.csv', 'wb') as csv_file:
      writer = csv.writer(csv_file)
      for row in statDict.values():
        writer.writerow(list(row))

    ## return statDict

def main(input_zone_polygon, input_value_raster):
    return loop_zonal_stats(input_zone_polygon, input_value_raster)


if __name__ == "__main__":

    #
    # Returns for each feature a dictionary item (FID) with the statistical values in the following order: Average, Mean, Medain, Standard Deviation, Variance, NumberofElements
    #
    # example run : $ python grid.py <full-path><output-shapefile-name>.shp xmin xmax ymin ymax gridHeight gridWidth
    # example run : ~/python_stuff/get_raster_stats_under_shapes.py anp_nacional_05_08_2016.shp peru_100m_dem_tif.tif
    #

    if len( sys.argv ) != 3:
        print "[ ERROR ] you must supply two arguments: input-zone-shapefile-name.shp input-value-raster-name.tif "
        sys.exit( 1 )
    print 'Returns for each feature a dictionary item (FID) with the statistical values in the following order: Mean, Median, Standard Deviation, Variance, NumberofElements'
    print main( sys.argv[1], sys.argv[2] )
