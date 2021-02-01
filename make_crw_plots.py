#!/usr/bin/env python3
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, WEEKLY, DateFormatter, rrulewrapper, WeekdayLocator, RRuleLocator, TU)
from matplotlib.backends.backend_pdf import PdfPages
from datetime import date, timedelta
import pandas as pd
import os, sys
import numpy as np
matplotlib.use('pdf')

infile = 'crw_noaa_alerts_daily.csv'
## SITE,DATE,SST_MIN,SST_MAX,SST@90th_HS,SSTA@90th_HS,90th_HS>0,DHW_from_90th_HS>1,BAA_7day_max

data = pd.read_csv(infile, sep=',', header=0)
str2date = lambda x: date(int(str(x)[0:4]), int(str(x)[4:6]), int(str(x)[6:]))
datelist = [ str2date(i) for i in data['DATE'] ]
data['mydate'] = datelist

formatter = DateFormatter('%m/%d/%y')
loc = WeekdayLocator(byweekday=TU, interval=1)
daydelta = timedelta(days=1)

stseries = date(2010, 1, 1)
endseries = date(2019, 12, 31)
span = endseries - stseries
watches = np.zeros(span.days, dtype=int)
warnings = np.zeros(span.days, dtype=int)
alert1 = np.zeros(span.days, dtype=int)
alert2 = np.zeros(span.days, dtype=int)
thedates = np.zeros(span.days, dtype='datetime64[D]')

for i in range(span.days): 
  thisdate = stseries + timedelta(days=i)
  index1 = np.logical_and(np.equal(data['BAA_7day_max'],1), np.equal(data['mydate'], thisdate))
  watches[i] = np.sum(index1)
  thedates[i] = thisdate
  index2 = np.logical_and(np.equal(data['BAA_7day_max'],2), np.equal(data['mydate'], thisdate))
  warnings[i] = np.sum(index2)
  index3 = np.logical_and(np.equal(data['BAA_7day_max'],3), np.equal(data['mydate'], thisdate))
  alert1[i] = np.sum(index3)
  index4 = np.logical_and(np.equal(data['BAA_7day_max'],4), np.equal(data['mydate'], thisdate))
  alert2[i] = np.sum(index4)
   

with PdfPages('noaa_crw_alert_timeseries.pdf') as pdf:
  fig = plt.figure(figsize=(10,8))
  ax = plt.subplot(1, 1, 1)
  ax.set_title('NOAA Coral Reef Watch Bleaching Events')
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=7)
  plt.plot(thedates, watches, fmt='--g', label='Watch')
  plt.plot(thedates, warnings, fmt='-g', label='Warning')
  plt.plot(thedates, alert1, fmt='--r', label='Alert 1')
  plt.plot(thedates, alert2, fmt='--r', label='Alert 2')
  plt.legend(loc='lower right')
  pdf.savefig(fig)

plt.close()

