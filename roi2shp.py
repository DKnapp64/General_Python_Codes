#!/usr/bin/env python2
import osgeo.ogr, osgeo.osr #we will need some packages
from osgeo import ogr #and one more for the creation of a new field
import gdal #and one more for the creation of a new field
import re
import sys, os
import itertools
import numpy as np
import pdb

def main(roi_text_file, utmzone, pixelsize, output_shapefile):
  
  utmzoneint = int(utmzone)
  if (utmzoneint < 0):
    epsgcode = 32700 + abs(utmzoneint)
  else:
    epsgcode = 32600 + utmzoneint
  
  inroitxt = roi_text_file
  
  f = open(inroitxt, "r")
  line = f.readline()
  
  roinames = []
  roinumpts = []
  numleft = 100
  
  while (numleft > 0):
    m = re.search('^; Number of ROIs:', line)
    if (m is not None):  
      numrois = int(line.strip()[(m.end(0)+1):])
      print numrois
      numleft = numrois
    n = re.search('; ROI name:', line)
    if (n is not None):
      roinames.append(line.strip()[(n.end(0)+1):])
      print roinames[-1]
    o = re.search('; ROI npts:', line)
    if (o is not None):
      roinumpts.append(int(line.strip()[(o.end(0)+1):]))
      print roinumpts[-1]
      numleft -= 1
      print numleft
    line = f.readline()
  
  f.close()
  
  startdata = (numrois * 4) + 5
  roistarts = [0] + roinumpts
  roiends = [0] + roinumpts
  for p in range(numrois):
    roistarts[p] = sum(roistarts[0:(p+1)]) + p
    roiends[p] = roistarts[p] + roinumpts[p]
    
  for p in range(numrois):
    roistarts[p] = roistarts[p] + startdata
    roiends[p] = roiends[p] + startdata
  
  roistarts = roistarts[0:numrois]
  roiends = roiends[0:numrois]
  
  print roistarts
  print roiends
  
  outRasterSRS = osgeo.osr.SpatialReference()
  outRasterSRS.ImportFromEPSG(epsgcode)
  
  drv = ogr.GetDriverByName("ESRI Shapefile")
  dst_ds = drv.CreateDataSource(output_shapefile)
  dst_layer = dst_ds.CreateLayer(os.path.splitext(os.path.basename(output_shapefile))[0], srs=outRasterSRS)
  newField = ogr.FieldDefn('MYFLD', ogr.OFTInteger)
  newFieldName = ogr.FieldDefn('ROINAME', ogr.OFTString)
  dst_layer.CreateField(newField)
  dst_layer.CreateField(newFieldName)
  
  for j in range(numrois):
    with open(inroitxt, "r") as f:
      lines = list(itertools.islice(f, roistarts[j]-1, roiends[j]-1))
      pixlin = np.zeros((roinumpts[j],2), dtype=np.int)
      utmxy = np.zeros((roinumpts[j],2), dtype=np.float64)
      for k,line in enumerate(lines):
        # parse each line to get pixel lines
        vals = line.split()
        pixlin[k,0] = int(vals[1])
        pixlin[k,1] = int(vals[2])
        utmxy[k,0] = float(vals[3])
        utmxy[k,1] = float(vals[4])
      
      xmin = min(pixlin[:,0])
      ymin = min(pixlin[:,1])
      xmax = max(pixlin[:,0])
      ymax = max(pixlin[:,1])
      utmxmin = min(utmxy[:,0])
      utmymin = min(utmxy[:,1])
      utmxmax = max(utmxy[:,0])
      utmymax = max(utmxy[:,1])
      newshape = [(xmax-xmin)+1,(ymax-ymin)+1]
      rasterdata = np.zeros((newshape[1],newshape[0]), dtype=np.uint8)
      junkx = (pixlin[:,0]-xmin)
      junky = (pixlin[:,1]-ymin)
      rasterdata[junky,junkx] = 1
      rastermem = gdal.GetDriverByName('MEM').Create('', newshape[0], newshape[1], 1, gdal.GDT_Byte) 
      rastermem.SetGeoTransform((utmxmin, float(pixelsize), 0, utmymax, 0, -float(pixelsize)))
      band = rastermem.GetRasterBand(1)
      mask = band
      band.WriteArray(rasterdata)
      rastermem.SetProjection(outRasterSRS.ExportToWkt())
      band.FlushCache()
      gdal.Polygonize(band, mask, dst_layer, 0, [], callback=None)
      band = None
      mask = None
      
  dst_ds.Destroy() #lets close the shapefile and reopen to add roinames
  
  ## Update layer with ROI Names
  drv2 = ogr.GetDriverByName("ESRI Shapefile")
  dst_ds2 = drv2.Open(output_shapefile, 1)
  layer = dst_ds2.GetLayer()
  
  for j,thisfeature in enumerate(layer):
    thisfeature.SetField('ROINAME', roinames[j])
    layer.SetFeature(thisfeature)
    print roinames[j]
  
  dst_ds2.Destroy()
  
  poly = None
  feature = None

if __name__ == "__main__":

    #
    # Returns a shapefile from an ASCII text output of an ROI from ENVI
    #
    # example run : $ roi2shp.py roi_text_file utmzone pixelsize output_shapefile
    #

  if len( sys.argv ) != 5:
    print "[ USAGE ] you must supply 4 arguments: roi_text_file utmzone pixelsize output_shapefile"
    print "example : roi2shp.py roi_text_file utmzone pixelsize output_shapefile"
    print ""
    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )
