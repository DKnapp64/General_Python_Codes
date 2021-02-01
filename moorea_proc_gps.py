#!/bin/env python3
import ogr, osr
import pyproj
import math
import numpy as np
import datetime
import os, sys
import re, fnmatch
import csv

def givedt(dt):
  mydt = datetime.datetime(dt[0], dt[1], dt[2], dt[3], dt[4], int(dt[5]))
  return mydt.strftime("%Y-%m-%d %H:%M:%S")

def main(ingpxfile, outpntsshapefile, secdiff):
  ## infile = "GPSTrack_D5T4.gpx"
  ## outfile = "GPSTrack_D5T4_utm6_with_segments.shp"

  ## Read in time data for each ASD file.
  ## they are stored in a pre-made list with the ASD file name and the date/Time in each row
  ## csvtablefile = "/Carnegie/DGE/caodata/Scratch/dknapp/ASD/Spectroscopy/list_clean_spec_time.txt"
  csvtablefile = "/Carnegie/DGE/caodata/Scratch/dknapp/ASD/Spectroscopy/list_spec_time.txt"
  specrows = []
  with open(csvtablefile, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
      specrows.append(row)

  transroot = os.path.splitext(ingpxfile)[0][-4:] + "*.asd.ref"

  ## Create a list with the date/times as datetime objects.
  spectimedates = []
  for row in specrows:
    ## uggh.  The format for timezone offset (%z) does not include a colon (:), 
    ## so we have to skip that colon character.
    temp = row[1][0:22] + row[1][23:]
    trydate = datetime.datetime.strptime(temp, "%Y-%m-%dT%H:%M:%S%z")
    spectimedates.append(trydate)

  ## CReate output spatial reference for Moorea (UTM Zone 6 South)
  spatialReference = osr.SpatialReference()
  spatialReference.ImportFromEPSG(32706)
  
  ## Create output data file
  drv = ogr.GetDriverByName("ESRI Shapefile")
  outDS = drv.CreateDataSource(outpntsshapefile)
  ##  outlayer = outDS.CreateLayer('moorea', spatialReference, ogr.wkbLineString)
  outlayer = outDS.CreateLayer('moorea', spatialReference, ogr.wkbPoint)
  outlayerDefn = outlayer.GetLayerDefn()
  tnameDefn = ogr.FieldDefn('specname', ogr.OFTString)
  timepntDefn = ogr.FieldDefn('timepnt', ogr.OFTString)
  outlayer.CreateField(tnameDefn)
  outlayer.CreateField(timepntDefn)
  
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


  for j in np.arange(0, (len(pntutm)-1)):
    pnt1 = pntutm[j]
    pnt2 = pntutm[j+1]
    diffx = pnt2[0] - pnt1[0]
    diffy = pnt2[1] - pnt1[1]
    initial_azimuth = math.degrees(math.atan2(diffx, diffy))
    azimuth = (initial_azimuth + 360) % 360
    azimuths.append(azimuth)
    gpstime1 = gpstimes[j]
    gpstime2 = gpstimes[j+1]
    segtimediff = (gpstime2-gpstime1).total_seconds()
    segdist = math.sqrt(math.pow(diffx,2) + math.pow(diffy,2))
    ## Find the spectra that are between these 2 points
    myregex = fnmatch.translate(transroot)
    asdobj = re.compile(myregex)

    for i,asdrow in enumerate(specrows):
      gotit = asdobj.match(asdrow[0])
      if gotit is not None:
        spectime = spectimedates[i] + datetime.timedelta(seconds=secdiff)
        #  is it between these 2 segment points?
        if (spectime > gpstime1) and (spectime < gpstime2):
          propo = ((spectime-gpstime1).total_seconds())/float(segtimediff)
          azrad = azimuth * (math.pi/180.0)
          xlen = math.sin(azrad) * (propo * segdist)
          ylen = math.cos(azrad) * (propo * segdist)
          xnewpnt = pnt1[0] + xlen
          ynewpnt = pnt1[1] + ylen
          feature = ogr.Feature(outlayerDefn)
          pnt = ogr.Geometry(ogr.wkbPoint)
          pnt.AddPoint(xnewpnt, ynewpnt)
          feature.SetGeometry(pnt)
          feature.SetFID(i)
          feature.SetField('specname', asdrow[0])
          timestr = spectime.astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ")
          feature.SetField('timepnt', timestr)
          outlayer.CreateFeature(feature)
    
  inDS, outDS = None, None

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ ERROR ] you must supply 3 arguments: moorea_grid_asd.py ingpxfile outpntsshapefile secdiff")
    print("where:")
    print("    inimgtemplate = the input gpxfile.")
    print("    outpntsshapefile = the output Shapefile with points for the various spectrometer readings.")
    print("                   The point locations are interpolated based on time between segment points.")
    print("    secdiff = the number of seconds to shift (plus or minus) the times of the ASD.")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], int(sys.argv[3]) )

