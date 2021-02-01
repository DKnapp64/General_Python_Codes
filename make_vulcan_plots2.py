#!/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, WEEKLY, DateFormatter, rrulewrapper, RRuleLocator)
from matplotlib.backends.backend_pdf import PdfPages
from datetime import date
import sys

data = np.genfromtxt("moorea_sample_coral_output_rb_20190811.csv", delimiter=',')
## infiles = ['20190406_moorea_tile_sr_rb.tif', '20190407_moorea_tile_sr_rb.tif', '20190415_moorea_tile_sr_rb.tif',
## '20190507_moorea_tile_sr_rb.tif', '20190517_moorea_tile_sr_rb.tif', '20190603_moorea_tile_sr_rb.tif',
## '20190604_moorea_tile_sr_rb.tif', '20190607_moorea_tile_sr_rb.tif', '20190616_moorea_tile_sr_rb.tif']

## tdates = ['20170421', '20170423', '20170505', '20170628', '20170720', '20170721',
## '20180112', '20180120', '20180125', '20180221', '20180223', '20180227',
## '20180228', '20180301', '20180302', '20180305', '20180712', '20180720',
## '20180723', '20180724', '20180727', '20180728', '20180807', '20180814',
## '20180818', '20180819', '20180823', '20180830', '20180905', '20180915',
## '20180920', '20181005', '20181008', '20181017', '20181101', '20181110',
## '20181111', '20181122', '20181129', '20181130', '20181204', '20181214',
## '20181223', '20181229', '20181230', '20190115', '20190117', '20190118',
## '20190123', '20190208', '20190227', '20190301', '20190307', '20190318',
## '20190322', '20190405', '20190406', '20190407', '20190415',
## '20190507', '20190517', '20190604',
## '20190607', '20190616']
## 
## tdates = ['20181230', '20190115', '20190117', '20190118',
## '20190123', '20190208', '20190227', '20190301', '20190307', '20190318',
## '20190322', '20190405', '20190406', '20190407', '20190415',
## '20190507', '20190517', '20190604',
## '20190607', '20190616']
## thedates = []
## for thisdate in tdates:
##   thedates.append(date(int(thisdate[0:4]), int(thisdate[4:6]), int(thisdate[6:8])))

## thedates = [date(2019,4,6), date(2019,4,7), date(2019,4,15), date(2019,5,7), date(2019,5,17), 
##   date(2019,6,4), date(2019,6,7), date(2019,6,16)]
## thedates = [date(2019,4,6), date(2019,4,7), date(2019,4,15), date(2019,5,7), date(2019,5,17), date(2019,6,3), 
##   date(2019,6,4), date(2019,6,7), date(2019,6,16)]
thedates = [date(2019,4,6), date(2019,4,7), date(2019,4,15), date(2019,5,7), date(2019,5,17), date(2019,6,3), 
  date(2019,6,4), date(2019,6,7), date(2019,6,16)]
## thedates = [date(2019,4,6), date(2019,4,7), date(2019,4,15), date(2019,5,7), date(2019,5,17), date(2019,6,4), date(2019,6,7), date(2019,6,16)]

rule = rrulewrapper(WEEKLY, interval=1)
loc = RRuleLocator(rule)
formatter = DateFormatter('%m/%d/%y')

## thedates = thedates[44:]

with PdfPages('coral_brightening_rb_rev20190811.pdf') as pdf:
  ## Page 1, Blue
  fig = plt.figure(figsize=(8,10))

  ax = plt.subplot(2, 1, 1)
  ax.set_title('Coral Brightening in Blue')
  plt.plot_date(thedates, data[0,0:9], 'b')
  plt.plot_date(thedates, data[2,0:9], 'b')
  plt.plot_date(thedates, data[4,0:9], 'b')
  plt.plot_date(thedates, data[6,0:9], 'b')
  plt.plot_date(thedates, data[8,0:9], 'b')
  plt.plot_date(thedates, data[10,0:9], 'b')
  plt.plot_date(thedates, data[12,0:9], 'b')
  plt.plot_date(thedates, data[14,0:9], 'b')
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=10)
  ax.set_ylabel('Reflectance %')
  
  ax = plt.subplot(2, 1, 2)
  ax.set_title('Coral Brightening in Green')
  plt.plot_date(thedates, data[1,0:9], 'g')
  plt.plot_date(thedates, data[3,0:9], 'g')
  plt.plot_date(thedates, data[5,0:9], 'g')
  plt.plot_date(thedates, data[7,0:9], 'g')
  plt.plot_date(thedates, data[9,0:9], 'g')
  plt.plot_date(thedates, data[11,0:9], 'g')
  plt.plot_date(thedates, data[13,0:9], 'g')
  plt.plot_date(thedates, data[15,0:9], 'g')
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=10)
  ax.set_ylabel('Reflectance %')
  pdf.savefig(fig)
  plt.close()

  ## d = pdf.infodict()
  ## d['Title'] = 'Coral Brightening at Moorea (May-Jun 2019)'
  ## d['Author'] = 'David Knapp'
  ## d['Subject'] = 'Allen Coral Atlas'
  ## d['CreationDate'] = date(2019, 7, 3)
  ## d['ModDate'] = date.today()

