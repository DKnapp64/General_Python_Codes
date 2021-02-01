#!/bin/env python3
import ogr, osr
import numpy as np
import math
import pyproj
import datetime
import os, sys
import re, fnmatch
import csv
import spectral
import copy

def main(ingpxfile, outlineshapefile, inspeclib, outspeclib, secdiff):

  img = spectral.envi.open(os.path.splitext(inspeclib)[0]+".hdr", inspeclib)
  specs = img.spectra
  specnames = img.names
  b400 = np.argmin(abs(np.asarray(img.bands.centers)-400))
  b700 = np.argmin(abs(np.asarray(img.bands.centers)-700))

  specidnums = np.zeros(len(specnames), dtype=np.int) 
  for k in range(len(specnames)):
    specidnums[k] = int(specnames[k][4:9])

  segids = specidnums//100
  segidsunique = np.unique(segids)

  specrows = []

  for row in specnames:
    vals = row.split()
    specrows.append(vals)

  ## Create a list with the date/times as datetime objects.
  spectimedates = []

  for row in specrows:
    ## uggh.  The format for timezone offset (%z) does not include a colon (:), 
    ## so we have to skip that colon character.
    temp = row[1][0:22] + row[1][23:]
    trydate = datetime.datetime.strptime(temp, "%Y-%m-%dT%H:%M:%S%z")
    spectimedates.append(trydate)

  ## Create output spatial reference for Moorea (UTM Zone 6 South)
  spatialReference = osr.SpatialReference()
  spatialReference.ImportFromEPSG(32706)
  
  ## Create output data file
  drv = ogr.GetDriverByName("ESRI Shapefile")
  outDS = drv.CreateDataSource(outlineshapefile)
  outlayer = outDS.CreateLayer('moorea', spatialReference, ogr.wkbLineString)
  outlayerDefn = outlayer.GetLayerDefn()
  tnameDefn = ogr.FieldDefn('specname', ogr.OFTString)
  time1pntDefn = ogr.FieldDefn('starttime', ogr.OFTString)
  time2pntDefn = ogr.FieldDefn('endtime', ogr.OFTString)
  outlayer.CreateField(tnameDefn)
  outlayer.CreateField(time1pntDefn)
  outlayer.CreateField(time2pntDefn)
  
  ## Get input data layer (track_points)
  inDS = ogr.Open(ingpxfile)
  lyr = inDS.GetLayerByName('track_points')
  lyrdefn = lyr.GetLayerDefn()
  numpnts = lyr.GetFeatureCount()
  fldcnt = lyrdefn.GetFieldCount()
  
  projutm6s = pyproj.Proj("+init=EPSG:32706")
  
  pntutm = []
  gpstimes = []
  azimuths = []
  
  lyr.ResetReading()

  ## create utc and french polynesia timezone objects
  utc = datetime.timezone.utc
  fptz = datetime.timezone(datetime.timedelta(hours=-10))
  
  for k in range(0,numpnts):
    feat = lyr.GetFeature(k)
    mytime = feat.GetFieldAsDateTime('time')
    print(mytime)
    mydatetime = datetime.datetime(mytime[0], mytime[1], mytime[2], mytime[3], \
      mytime[4], int(mytime[5]), tzinfo=utc)
    geom = feat.GetGeometryRef()
    lon = geom.GetX()
    lat = geom.GetY()
    temputm = projutm6s(lon, lat)
    pntutm.append(temputm)
    gpstimes.append(mydatetime)

  ## divide up by spectral segments
  for g in segidsunique:
    index = np.equal(segids, g)
    ## if (index.sum() == 0):
    ##   continue
    segspecs = specs[np.where(index)[0],:]
    segspecnames = (np.asarray(specnames)[np.where(index)[0]]).tolist()
    segspectimes = np.asarray(spectimedates)[np.where(index)[0]]
    
    feature = ogr.Feature(outlayerDefn)
    line = ogr.Geometry(ogr.wkbLineString)
    
    for f,thename in enumerate(segspecnames):
      spectime = segspectimes[f] + datetime.timedelta(seconds=secdiff)
      for d in range(len(gpstimes)-1):
        if (spectime > gpstimes[d]) and (spectime < gpstimes[d+1]):
          tind = d
      if (f == 0):
        oldtind = tind
      pnt1 = pntutm[tind]
      pnt2 = pntutm[tind+1]
      gpstime1 = gpstimes[tind]
      gpstime2 = gpstimes[tind+1]
      segtimediff = (gpstime2-gpstime1).total_seconds()
      diffx = pnt2[0] - pnt1[0]
      diffy = pnt2[1] - pnt1[1]
      initial_azimuth = math.degrees(math.atan2(diffx, diffy))
      azimuth = (initial_azimuth + 360) % 360
      azrad = azimuth * (math.pi/180.0)
      segdist = math.sqrt(math.pow(diffx,2) + math.pow(diffy,2))
      propo = ((spectime-gpstime1).total_seconds())/float(segtimediff)
      xlen = math.sin(azrad) * (propo * segdist)
      ylen = math.cos(azrad) * (propo * segdist)
      xnewpnt = pnt1[0] + xlen
      ynewpnt = pnt1[1] + ylen
      line.AddPoint_2D(xnewpnt, ynewpnt)
      if (oldtind > tind):
        line.AddPoint_2D(pnt2[0], pnt2[1])
        oldtind = tind
      if (f == 0):
        time1 = spectime 

    print("Start: %s    End: %s" % (time1.astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ"), spectime.astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
    ## OK, all the points for the segment are in.  Now, set attributes and add to layer.
    feature.SetGeometry(line)
    feature.SetFID(g)
    feature.SetField('specname', ("Mean_Seg%03d_N%03d_" % (g, len(segspecnames)))+os.path.splitext(ingpxfile)[0][-4:])
    timestr1 = time1.astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    timestr2 = spectime.astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    feature.SetField('starttime', timestr1)
    feature.SetField('endtime', timestr2)
    outlayer.CreateFeature(feature)
      
  inDS, outDS = None, None

if __name__ == "__main__":

  if len( sys.argv ) != 6:
    print("[ ERROR ] you must supply 5 arguments: moorea_proc_gps4.py ingpxfile outshapefile inspeclib outspeclib secdiff")
    print("where:")
    print("    ingpxfile = the input GPX file with a track_points layer")
    print("    outshapefile = the output Shapefile with points for the various spectrometer readings.")
    print("                   The point locations are interpolated based on time between segment points.")
    print("    inspeclib = the input spectral library")
    print("    outspeclib = the output spectral library prefix for making out mean and sdev libraries")
    print("    secdiff = the number of seconds to add to the ASD measurement time to sync better with GPS time.")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]) )
