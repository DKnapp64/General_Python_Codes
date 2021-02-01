#!/bin/env python3
import gdal
import osr
import os, sys
import numpy as np
import subprocess
import copy
from datetime import datetime, timedelta
import glob
import shutil

def main(indir, minstart):
  
  today = datetime.today()
  todaytxt = today.strftime('%Y%m%d')
  thedates = [minstart]
  start = datetime.strptime(minstart, '%Y%m%d')

  thisday = start + timedelta(days=2)

  while thisday < today:
    thedates.append(thisday.strftime('%Y%m%d'))
    thisday += timedelta(days=1)

  reprojlist = []

  if not os.path.exists(indir):
    print("Directory %s does not exist" % (indir))
    sys.exit(0)

  for thisdate in thedates:
    srlist = glob.glob(indir+os.path.sep+thisdate+"*_SR.tif")
    udm2list = glob.glob(indir+os.path.sep+thisdate+"*_udm2.tif")
    imglist = srlist + udm2list
    if (len(imglist) > 0):
      for myimg in imglist:
        tmpDS = gdal.Open(myimg, gdal.GA_ReadOnly)
        thisproj = tmpDS.GetProjectionRef()
        myosr = osr.SpatialReference()
        myosr.ImportFromWkt(thisproj)
        thecode = int(myosr.GetAttrValue("AUTHORITY", 1))
        if (thecode != 32605):
          reprojlist.append(myimg)
        tmpDS = None

  if (len(reprojlist) == 0):
    print("No images needing reprojection found")
    sys.exit(0)

  ## gdalbase = ['srun','-n','1','-c','4','--mem=32000','~/.conda/envs/davekenv/bin/gdalwarp','-of','GTiff','-t_srs','EPSG:32605','-tr','3.0','3.0','-tap']
  gdalbase = ['/home/dknapp4/.conda/envs/davekenv/bin/gdalwarp','-of','GTiff','-t_srs','EPSG:32605','-tr','3.0','3.0','-tap']
  
  wrkdir = '/scratch/dknapp4/Intensive/WestHawaii/utm4to5'
  if not os.path.exists(wrkdir):
    os.mkdir(wrkdir) 

  ## reprojlist = reprojlist[0]

  if (len(reprojlist) == 0):
    print("No Images outside of zone 5 found.\nNothing to do.")
    sys.exit(0)

  for img in reprojlist:
    gdalnew = copy.copy(gdalbase)
    gdalnew.extend([img, wrkdir+os.path.sep+os.path.basename(os.path.splitext(img)[0])+'_utm5.tif']) 
    try:
      completed = subprocess.run(gdalnew, check=True)
    except subprocess.CalledProcessError as e:
      print(e.output)
    if (completed.returncode == 0):
      shutil.move(wrkdir+os.path.sep+os.path.basename(os.path.splitext(img)[0])+'_utm5.tif', img)
    print("File: %s reprojected to UTM 5" % (img))
    print(" ".join(gdalnew))

if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ USAGE ] you must supply 2 arguments: reproj4to5.py indir startdate")
    print("     indir: the directory in which to search for images of UTM 4")
    print("     startdate: The startdate in YYYYMMDD format at which to start looking for images of zone UTM4 for reprojection to UTM5")
    print("")
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2] )

