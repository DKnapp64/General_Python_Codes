#!/bin/env python3
import gdal
import pandas as pd
import numpy as np
import os, sys

def main(ascdesc, tileid, startdate, enddate):
  inpickle = 'dfnew_'+tileid+'_'+startdate+'_to_'+enddate+'.pkl'
  
  df2 = pd.read_pickle(inpickle)
  
  good = (df2['y'] != -9999.0)
  df3 = df2[good]
  indata = df3[['Id', 'y', 'sd', 'n']].to_numpy()
  
  ## for each patch, run prophet
  undates = np.unique(df3['ds'])
  numdates = undates.shape[0]
  uniqids = np.unique(df3['Id']).astype(np.int)
  holdarr = np.zeros((256,256, numdates), dtype=np.uint8)
  anom = np.zeros(indata.shape[0], dtype=np.uint8)
  outmedian = np.zeros(uniqids.shape[0])
  
  for j,thisds in enumerate(uniqids):
    index = np.logical_and(np.equal(indata[:,0], thisds), np.greater(indata[:,1], 0))
    if (np.sum(index) > 0):
      med = np.median(indata[:,1][index])
      diff = (np.absolute(indata[:,1][index] - med) > np.std(indata[:,1][index]))
      if (np.sum(diff) > 0):
        anom[np.nonzero(index)[0][diff]] = 1
  
  print('%d patches to work through' % (uniqids.shape[0]))
  
  for i in range(indata.shape[0]):
    theid = int(indata[i,0])
    if (anom[i] == 1):
      rowsub = theid//256 
      colsub = theid % 256 
      datesub = df3['ds'].to_numpy()[i]
      for j,thisds in enumerate(undates):
        band = np.nonzero(np.equal(undates, datesub))[0][0]
      holdarr[rowsub, colsub, band] = 1
    if ((i%1000) == 0):
      print("Finished %d of %d" % (i+1, indata.shape[0]))
  
  np.save('anomaly_simple_'+tileid+'_coarse_array.npy', holdarr)
  
  drv = gdal.GetDriverByName('GTiff')
  outDS = drv.Create('anomasksimple_'+tileid+'.tif', 256, 256, numdates, gdal.GDT_Byte)
  for k in range(numdates):
    outDS.GetRasterBand(k+1).WriteArray(np.squeeze(holdarr[:,:,k]))
  
  tmpDS = gdal.Open('/scratch/dknapp4/Hawaii_Weekly/AscendingDescending/descending_20190429_to_20190506/'+tileid+'_br_comp.tif', gdal.GA_ReadOnly)
  gt = tmpDS.GetGeoTransform()
  newgt = (gt[0], gt[1]*16, gt[2], gt[3], gt[4], gt[5]*16)
  proj = tmpDS.GetProjection()
  outDS.FlushCache()
  outDS.SetProjection(proj)
  outDS.SetGeoTransform(newgt)
  
  tmpDS, outDS = None, None
  print("All done")

if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print("[ USAGE ] you must supply 4 arguments: simple_anom.py ascdesc tileid startdate enddate")
    print("     ascdesc = 'ascending' or 'descending'")
    print("     tileid = in the form of 'L15-0126E-1148N'")
    print("     startdate = '20190429'  date in the form 'YYYYMMDD', which MUST BE THE MONDAY OF THE WEEK")
    print("     enddate = '20191202'  date in the form 'YYYYMMDD', which MUST BE THE MONDAY OF THE WEEK")
    print("")
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )
