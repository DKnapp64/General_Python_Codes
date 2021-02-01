#!/usr/bin/env python3
import gdal
import pandas as pd
import numpy as np
import os, sys
import math
from datetime import date, timedelta

def main(ascdesc, tileid, startdate, enddate):
  ## example inputs
  ## ascdesc = 'ascending' or 'descending'
  ## tileid = in the form of 'L15-0126E-1148N'
  ## startdate = '20190429'  date in the form 'YYYMMDD', which MUST BE THE MONDAY OF THE WEEK
  ## enddate = '20191202'  date in the form 'YYYMMDD', which MUST BE THE MONDAY OF THE WEEK

  startit = date(int(startdate[0:4]), int(startdate[4:6]), int(startdate[6:8]))
  endit = date(int(enddate[0:4]), int(enddate[4:6]), int(enddate[6:8]))
  timediff = endit - startit
  numweeks = int(timediff.days/7.0)
  thedates = []

  ## build the names of the Starting and Ending weeks based on the dates given
  ## Again, this is based on the Monday being the Start/End of the weeks
  for week in range(numweeks):
    sw = startit + timedelta(days=week*7)
    ew = startit + timedelta(days=(week+1)*7)
    thedates.append(sw.strftime('%Y%m%d') + '_to_' + ew.strftime('%Y%m%d'))
    
  ## Based on the tileid, build the names of the Rb image to use and the 
  ## corresponding Coral Mask
  inimage = tileid + '_br_comp.tif'
  incoral = tileid + '_coral.tif'

  bdir = '/scratch/dknapp4/Hawaii_Weekly/AscendingDescending/'
  coralDS = gdal.Open(bdir+'CoralNew'+os.path.sep+incoral, gdal.GA_ReadOnly)
  coral = coralDS.GetRasterBand(1).ReadAsArray()
  
  ## Get the first image in the time series.  The size is assumed to be
  ## the same (i.e., 4096 x 4096)
  tempimage = bdir+ascdesc+'_'+thedates[0]+os.path.sep+inimage 
  inDS = gdal.Open(tempimage, gdal.GA_ReadOnly)
  xsize = inDS.RasterXSize
  ysize = inDS.RasterYSize
  
  inDS, coralDS = None, None
  
  nrows = math.floor(ysize/16)
  ncols = math.floor(xsize/16)
  
  columns = ['Id', 'ds', 'y', 'sd', 'n']
  
  ## create the DataFrame to hold the data
  df = pd.DataFrame(columns=columns)
  df.Id = df.Id.astype(np.int64)
  df.ds = df.ds.astype(np.str)
  df.y = df.y.astype(np.float64)
  df.sd = df.sd.astype(np.float64)
  df.n = df.n.astype(np.float64)
  
  ## go through the various weeks of data and process the 16x16 patches in each image
  ## record the means in the data frame.  At each iteration, save the data frame to a pickle
  ## so that it can be reloaded.
  ##
  for thisdate in thedates:
    print(thisdate)
    ## Generate justdate, which is the Tuesday that the new data are compiled and
    ## corresponds to the previous week of data
    justdate = date(int(thisdate[-8:-4]), int(thisdate[-4:-2]), int(thisdate[-2:])) + timedelta(days=1) 
    thisimage = bdir+ascdesc+'_'+thisdate+os.path.sep+inimage 
    if os.path.exists(thisimage):
      print(thisimage)
      inDS = gdal.Open(thisimage, gdal.GA_ReadOnly)
    else:
      print('The image %s does not exist' % (thisimage))
      continue
    data = inDS.GetRasterBand(1).ReadAsArray()
    good1 = np.logical_and(np.not_equal(data, -9999), np.not_equal(data, 0))
    good2 = np.logical_and(good1, np.equal(coral, 1))
    templist = []
    for i in range(nrows):
      for j in range(ncols):
        sub = data[i*16:(i+1)*16, j*16:(j+1)*16]
        g = good2[i*16:(i+1)*16, j*16:(j+1)*16]
        if (np.sum(g) == 0):
          templist.append({'Id' : (i*256+j), 'ds' : justdate.strftime('%Y-%m-%d'), 'y': -9999.0, 'sd': -9999.0, 'n':-9999.0})
          ## df = df.append({'Id' : (i*256+j), 'ds' : justdate.strftime('%Y-%m-%d'), 
          ##   'y': -9999.0}, ignore_index=True)
          continue
        mn = np.mean(sub[g])/10000.0
        sdev = np.std(sub[g])/10000.0
        ## df = df.append({'Id' : (i*256+j), 'ds' : justdate.strftime('%Y-%m-%d'), 'y': mn}, ignore_index=True)
        templist.append({'Id' : (i*256+j), 'ds' : justdate.strftime('%Y-%m-%d'), 'y': mn, 'sd': sdev, 'n': np.sum(g)})
    df = pd.concat((df, pd.DataFrame(templist)), ignore_index=True, sort=True)
    inDS = None
    df.to_pickle('dfnew_'+tileid+'_'+startdate+'_to_'+enddate+'.pkl')


if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print("[ USAGE ] you must supply 4 arguments: make_df_from_image.py ascdesc tileid startdate enddate")
    print("     ascdesc = 'ascending' or 'descending'")
    print("     tileid = in the form of 'L15-0126E-1148N'")
    print("     startdate = '20190429'  date in the form 'YYYYMMDD', which MUST BE THE MONDAY OF THE WEEK")
    print("     enddate = '20191202'  date in the form 'YYYYMMDD', which MUST BE THE MONDAY OF THE WEEK")
    print("")
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )

