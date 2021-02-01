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

def givedt(dt):
  mydt = datetime.datetime(dt[0], dt[1], dt[2], dt[3], dt[4], int(dt[5]))
  return mydt.strftime("%Y-%m-%d %H:%M:%S")

def main(ingpxfile, outlineshapefile, inspeclib, outspeclib, secdiff):

  img = spectral.envi.open(os.path.splitext(inspeclib)[0]+".hdr", inspeclib)
  specs = img.spectra
  specnames = img.names
  b400 = np.argmin(abs(np.asarray(img.bands.centers)-400))
  b700 = np.argmin(abs(np.asarray(img.bands.centers)-700))

  ## infile = "GPSTrack_D5T4.gpx"
  ## outfile = "GPSTrack_D5T4_utm6_with_segments.shp"

  ## Read in time data for each ASD file.
  ## they are stored in a pre-made list with the ASD file name and the date/Time in each row
  ## csvtablefile = "/Carnegie/DGE/caodata/Scratch/dknapp/ASD/Spectroscopy/list_spec_time.txt"

  specrows = []

  ## with open(csvtablefile, 'r') as csvfile:
  ##   csvreader = csv.reader(csvfile)
  ##   for row in csvreader:
  ##     specrows.append(row)

  for row in specnames:
    vals = row.split()
    specrows.append(vals)

  transroot = os.path.splitext(ingpxfile)[0][-4:] + "*.asd.ref"

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
  ##  outlayer = outDS.CreateLayer('moorea', spatialReference, ogr.wkbLineString)
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
  times = []
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
    times.append(mydatetime)

  segspecmeans = np.zeros((len(pntutm)-1, b700-b400+1), dtype=np.float32)
  segspecsdevs = np.zeros((len(pntutm)-1, b700-b400+1), dtype=np.float32)

  meanspeclib = copy.deepcopy(img)
  sdevspeclib = copy.deepcopy(img)
  segspecmeannames = []
  segspecsdevnames = []
  keep = []

  for j in np.arange(0, (len(pntutm)-1)):
    pnt1 = pntutm[j]
    pnt2 = pntutm[j+1]
    diffx = pnt2[0] - pnt1[0]
    diffy = pnt2[1] - pnt1[1]
    initial_azimuth = math.degrees(math.atan2(diffx, diffy))
    azimuth = (initial_azimuth + 360) % 360
    azimuths.append(azimuth)
    time1 = times[j]
    time2 = times[j+1]
    segtimediff = (time2-time1).total_seconds()
    segdist = math.sqrt(math.pow(diffx,2) + math.pow(diffy,2))
    ## Find the spectra that are between these 2 points
    myregex = fnmatch.translate(transroot)
    asdobj = re.compile(myregex)

    speclist = []
    specnamelist = []

    for i,asdrow in enumerate(specrows):
      gotit = asdobj.match(asdrow[0])
      if gotit is not None:
        spectime = spectimedates[i] + datetime.timedelta(seconds=secdiff)
        #  is it between these 2 segment points?
        if (spectime > time1) and (spectime < time2):
          speclist.append(specs[i,:])
          specnamelist.append(asdrow[0])
          ## propo = ((spectime-time1).total_seconds())/float(segtimediff)
          ## azrad = azimuth * (math.pi/180.0)
          ## xlen = math.sin(azrad) * (propo * segdist)
          ## ylen = math.cos(azrad) * (propo * segdist)
          ## xnewpnt = pnt1[0] + xlen
          ## ynewpnt = pnt1[1] + ylen

    numsegspecs = len(speclist)
    if (numsegspecs == 0):
      keep.append(False)
      continue
    else:
      keep.append(True)

    temparr = np.zeros((numsegspecs, specs.shape[1]), dtype=np.float32)
    for col in range(numsegspecs):
      temparr[col,:] = speclist[col]

    meanspec = np.mean(temparr, axis=0)
    sdevspec = np.std(temparr, axis=0)
    segspecmeans[j,:] = meanspec[b400:(b700+1)]
    segspecsdevs[j,:] = sdevspec[b400:(b700+1)]
    segspecmeannames.append(("Mean_Seg%03d_N%03d_" % (j, numsegspecs))+os.path.splitext(ingpxfile)[0][-4:])
    segspecsdevnames.append(("SD_Seg%03d_N%03d_" % (j, numsegspecs))+os.path.splitext(ingpxfile)[0][-4:])
    feature = ogr.Feature(outlayerDefn)
    line = ogr.Geometry(ogr.wkbLineString)
    line.AddPoint_2D(pnt1[0], pnt1[1])
    line.AddPoint_2D(pnt2[0], pnt2[1])
    feature.SetGeometry(line)
    feature.SetFID(j)
    feature.SetField('specname', ("Mean_Seg%03d_N%03d_" % (j, numsegspecs))+os.path.splitext(ingpxfile)[0][-4:])
    timestr1 = time1.astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    timestr2 = time2.astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    feature.SetField('starttime', timestr1)
    feature.SetField('endtime', timestr2)
    outlayer.CreateFeature(feature)
    
  inDS, outDS = None, None

  meanspeclib.spectra = segspecmeans[keep,:]
  meanspeclib.names = segspecmeannames
  meanspeclib.bands.centers = img.bands.centers[b400:(b700+1)]
  sdevspeclib.spectra = segspecsdevs[keep,:]
  sdevspeclib.names = segspecsdevnames
  sdevspeclib.bands.centers = img.bands.centers[b400:(b700+1)]

  meanspeclib.save(outspeclib+"_mean", description="Mean spectra by Segment")
  sdevspeclib.save(outspeclib+"_sdev", description="Standard Deviation spectra by Segment")

if __name__ == "__main__":

  if len( sys.argv ) != 6:
    print("[ ERROR ] you must supply 5 arguments: moorea_proc_gps3.py ingpxfile outshapefile inspeclib outspeclib secdiff")
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
