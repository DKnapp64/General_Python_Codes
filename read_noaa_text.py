#!/usr/bin/env python3
import pandas as pd
import os, sys
import glob
import datetime
import numpy as np

## Index(['YYYY', 'MM', 'DD', 'SST_MIN', 'SST_MAX', 'SST@90th_HS', 'SSTA@90th_HS',
##        '90th_HS>0', 'DHW_from_90th_HS>1', 'BAA_7day_max'],
##       dtype='object')

infiles = glob.glob("CRW_Virtual_Station_Summary_Stats/*.txt")
## infiles = infiles[0:5]

fout = open('crw_noaa_alerts.csv', 'w')

for thefile in infiles:
  f = open(thefile, 'r')
  templines = f.readlines(1000)
  staname = templines[1].strip() 
  f.close()
  data = pd.read_csv(thefile, skiprows=21, sep='\s+', header=0)
  mylist = [ datetime.datetime(data['YYYY'][i], data['MM'][i], data['DD'][i]) for i in range(data['YYYY'].shape[0]) ]
  data['date'] = mylist

  index = np.greater(data['BAA_7day_max'], 0)
  bleach = data[index]
  t1 = (bleach['date'][0:-1]).to_numpy().astype('datetime64')
  t2 = (bleach['date'][1:]).to_numpy().astype('datetime64')
  diffit  = t2 - t1
  index2 = np.equal(diffit.astype('timedelta64[D]').astype(np.int64), 1)
  rows = np.flatnonzero(index2)
  for j,ind in enumerate(rows[0:-1]):
    if (j == 0):
      starttime = bleach.iloc[ind]['date']
      stind = ind
      alertmax = 0
    elif (j > 0) and ((rows[j]-rows[j-1]) > 1):
      starttime = bleach.iloc[ind]['date']
      stind = ind
      alertmax = 0

    if (bleach.iloc[ind]['BAA_7day_max'] > alertmax):
      alertmax = bleach.iloc[ind]['BAA_7day_max']

    if ((rows[j+1]-rows[j]) > 1):
      endtime = bleach.iloc[ind]['date']
      endind = ind
      meansstmax = np.mean(bleach.iloc[stind:endind]['SST_MAX'])
      meanssta = np.mean(bleach.iloc[stind:endind]['SSTA@90th_HS'])
      meandhw = np.mean(bleach.iloc[stind:endind]['DHW_from_90th_HS>1'])
      fout.write('%s, %7.2f, %8.4f, %7.2f, %s, %s, %d\n' % (staname, meansstmax, meanssta, meandhw, starttime.strftime('%Y%m%d'), endtime.strftime('%Y%m%d'), alertmax))

  print('Finished file %s' % (thefile))
    
fout.close()

