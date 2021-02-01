#!/bin/env python3
import gdal
import numpy as np
import fnmatch, re
import datetime
import os, sys

def get_overlap_info(focal_bounds, focal_res, img_bounds, img_res):

  r1 = [focal_bounds[0], focal_bounds[3], focal_bounds[1], focal_bounds[2]]
  r2 = [img_bounds[0], img_bounds[3], img_bounds[1], img_bounds[2]]

  ## find intersection
  intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]

  ## Test for non-overlap.  if not overlapping, return -1s.
  if ((intersection[0] > intersection[2]) or (intersection[3] > intersection[1])):
    return((-1.0,-1.0,-1.0,-1.0), (-1.0,-1.0,-1.0,-1.0))
    
  # check for any overlap
  left1flt = (intersection[0]-r1[0])/focal_res # difference divided by pixel dimension
  left1 = int(np.abs(round((intersection[0]-r1[0])/focal_res))) # difference divided by pixel dimension
  top1flt = (intersection[1]-r1[1])/focal_res
  top1 = int(np.abs(round(((intersection[1]-r1[1])/focal_res))))
  col1 = int(np.abs(round(((intersection[2]-r1[0])/focal_res) - left1flt))) # difference minus offset left
  row1 = int(np.abs(round(((intersection[3]-r1[1])/focal_res) - top1flt)))
 
  left2flt = (intersection[0]-r2[0])/img_res # difference divided by pixel dimension
  left2 = int(np.abs(round(((intersection[0]-r2[0])/img_res)))) # difference divided by pixel dimension
  top2flt = (intersection[1]-r2[1])/img_res
  top2 = int(np.abs(round(((intersection[1]-r2[1])/img_res))))
  col2 = int(np.abs(round(((intersection[2]-r2[0])/img_res) - left2flt))) # difference minus new left offset
  row2 = int(np.abs(round(((intersection[3]-r2[1])/img_res) - top2flt)))
 
  ## print("%d   %d    %d   %d" % (left1,top1,col1,row1))
  ## print("%d   %d    %d   %d" % (left2,top2,col2,row2))

  return((left1,top1,col1,row1), (left2,top2,col2,row2))
 
def maketime(infile):

  basedove = os.path.basename(infile)
  year = int(basedove[0:4])
  month = int(basedove[4:6])
  day = int(basedove[6:8])
  hour = int(basedove[9:11])
  minute = int(basedove[11:13])
  second = int(basedove[13:15])
  
  if (len(basedove.split('_')[2]) == 4): 
    satellite = basedove.split('_')[2] 
    hms = basedove.split('_')[1] 
  else:
    if (len(basedove.split('_')[2]) == 1): 
      satellite = basedove.split('_')[3] 
      hms = basedove.split('_')[1] 

  imgdate = datetime.date(year, month, day).timetuple().tm_yday
  mytime = datetime.datetime(year, month, day, hour, minute, second)
  return mytime, satellite

def mosaic_dove(indovedir, focal_bounds):
  
  doveroot = '2*3B_AnalyticMS_SR.tif'
  doveregex = fnmatch.translate(doveroot)
  dovereobj = re.compile(doveregex)
  
  dovelist = []
  times = [] 
  sats = [] 
  
  filelist2 = os.listdir(indovedir)
  
  for dovefile in filelist2:
    gotit = dovereobj.match(dovefile)
    if gotit is not None:
      ## Does the file intersect area of interest?
      tmpDS = gdal.Open(dovefile, gdal.GA_ReadOnly)
      gt = tmpDS.GetGeoTransform()
      imgbnd = (gt[0], gt[0]+tmpDS.RasterXSize*gt[1], gt[3] + tmpDS.RasterYSize*gt[5], gt[3])
      myfocal, myimgbounds = get_overlap_info(focal_bounds, 3.0, imgbnd, img_res)
      srcDS = gdal.Open(dovefile, gdal.GA_ReadOnly)
      gt = srcDS.GetGeoTransform()
      ov = get_overlap
      thistime, thissatellite = maketime(dovefile)
      times.append(thistime)
      sats.append(thissatellite)
      dovelist.append(dovefile)

  ## find unique satellite ids using set comprehension
  uniqsats = { sat for sat in sats } 

  ## for each unique satellite id, make a sublist, sort by time and group
  f = open(outscriptfile, "w")

  for this in uniqsats:
    satindex = [i for i,x in enumerate(dovelist) if this in x]
    sublist = [dovelist[i] for i in satindex]
    sublistsort = sorted(sublist)

    countit = 0

    for j,name in enumerate(sublistsort):
      thistime, thissatellite = maketime(sublistsort[j])
      if (countit < 1):
        thistime, thissatellite = maketime(sublistsort[j])
        mylist = [sublistsort[j]]
        countit = 1
      else:
        thistime, thissatellite = maketime(sublistsort[j])
        lasttime, lastsatellite = maketime(sublistsort[j-1])
        if (thistime == (lasttime + datetime.timedelta(seconds=1))):
          mylist.append(sublistsort[j])
          countit += 1
        else:
          if (countit > 1):
            ## end of grouping, print out
            mylist = [sublistsort[j]]
            for k in mylist:
              print(("%s") % (k))
            print("END OF MOSAIC") 
            countit = 1
          else:
            print((" %s is a single image, no mosaicking needed.") % (sublistsort[j]))

    
  f.close()
    
if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ ERROR ] you must supply 2 arguments: mosaic_dove.py dovedir outmosaic")
    print("    dovedir = directory containing the Dove images (2*3B_AnalyticMS.tif) to get parameters for.")
    print("    outmosaic = the output CSV file with the Dove image file name and parameters")
    print("")

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2])
