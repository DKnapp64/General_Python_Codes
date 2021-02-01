#!/bin/env python3
import gdal
import numpy as np
from datetime import date, timedelta
import os, sys

def main(quadname, ascdesc, startdate, enddate, outfile):
  """This is a command line program for creating a multiband time series
     from the bottom reflectance from imagery of a particular quad.
  """ 

  ## Create start and end date objects
  sdate = date(int(startdate[0:4]), int(startdate[4:6]), int(startdate[6:]))
  edate = date(int(enddate[0:4]), int(enddate[4:6]), int(enddate[6:]))

  ## confirm that they are Mondays
  if ((sdate.weekday() != 0) or (edate.weekday() != 0)):
    print('Start Date and/or End Date is/are not a Monday')
    sys.exit(0)

  ##  build image names
  inimages = []
  difftime = edate - sdate

  ## how many weeks?
  numweeks = int(round(difftime.days/7.0))
  for i in range(numweeks):
    tempend = sdate + ((i+1) * timedelta(days=7))
    tempstart = sdate + (i * timedelta(days=7))
    nametemp = tempstart.strftime('%Y%m%d') + '_to_' + tempend.strftime('%Y%m%d')
    nametemp += os.path.sep + 'descending/' + quadname + '_br_comp.tif'
    if os.path.exists(nametemp):
      inimages.append(nametemp)

  numweeks = len(inimages)

  tempDS = gdal.Open(inimages[0], gdal.GA_ReadOnly)
  drv = gdal.GetDriverByName('GTiff')
  outDS = drv.Create(outfile, tempDS.RasterXSize, tempDS.RasterYSize, numweeks, eType=tempDS.GetRasterBand(1).DataType, options=['COMPRESS=LZW', 'TILED=YES'])
  outDS.SetGeoTransform(tempDS.GetGeoTransform())
  outDS.SetProjection(tempDS.GetProjection())
  tempDS = None

  for j in range(numweeks):
    endstring = inimages[j].split('/')[0][-8:]
    tDS = gdal.Open(inimages[j], gdal.GA_ReadOnly)
    data = tDS.GetRasterBand(1).ReadAsArray()
    outBand = outDS.GetRasterBand(j+1)
    outBand.WriteArray(data)
    outBand.SetDescription(endstring)
    outBand.FlushCache() 
    tDS = None
    print(endstring)
  
  outDS = None

if __name__ == "__main__":

  if len( sys.argv ) != 6:
    print("[ USAGE ] you must supply two arguments: make_aca_temporal_stack.py quadname ascdesc startdate enddate outfile")
    print("     quadname: the quad to process")
    print("     ascdesc: ascending or descending")
    print("     startdate: the startdate to use for gathering image datah")
    print("     enddate: the enddate to use for gathering image datah")
    print("     outname: the multiband output file")
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] )

