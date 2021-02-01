#!/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (WEEKLY, DateFormatter, rrulewrapper, RRuleLocator)
from matplotlib.backends.backend_pdf import PdfPages
from datetime import date
import sys

data = np.genfromtxt("moorea_sample_coral_output_20190710.csv", delimiter=',')

## thedates = [date(2019,4,6), date(2019,4,7), date(2019,4,15), date(2019,5,7), date(2019,5,17), date(2019,6,3), 
##   date(2019,6,4), date(2019,6,7), date(2019,6,16)]
thedates = [date(2019,4,6), date(2019,4,7), date(2019,4,15), date(2019,5,7), date(2019,5,17), date(2019,6,4), date(2019,6,7), date(2019,6,16)]

rule = rrulewrapper(WEEKLY, interval=1)
loc = RRuleLocator(rule)
formatter = DateFormatter('%m/%d/%y')

with PdfPages('coral_brightening_rev20190710b.pdf') as pdf:
  ## Page 1, Red
  fig = plt.figure(figsize=(8,10))

  ax = plt.subplot(2, 1, 1)
  ax.set_title('Coral Brightening in Blue')
  ## plt.plot_date(thedates, data[0,0:9], 'b')
  ## plt.plot_date(thedates, data[2,0:9], 'b')
  ## plt.plot_date(thedates, data[4,0:9], 'b')
  ## plt.plot_date(thedates, data[6,0:9], 'b')
  ## plt.plot_date(thedates, data[8,0:9], 'b')
  ## plt.plot_date(thedates, data[10,0:9], 'b')
  ## plt.plot_date(thedates, data[12,0:9], 'b')
  ## plt.plot_date(thedates, data[14,0:9], 'b')
  plt.plot_date(thedates, data[0,[0,1,2,3,4,6,7,8]], 'b')
  plt.plot_date(thedates, data[2,[0,1,2,3,4,6,7,8]], 'b')
  plt.plot_date(thedates, data[4,[0,1,2,3,4,6,7,8]], 'b')
  plt.plot_date(thedates, data[6,[0,1,2,3,4,6,7,8]], 'b')
  plt.plot_date(thedates, data[8,[0,1,2,3,4,6,7,8]], 'b')
  plt.plot_date(thedates, data[10,[0,1,2,3,4,6,7,8]], 'b')
  plt.plot_date(thedates, data[12,[0,1,2,3,4,6,7,8]], 'b')
  plt.plot_date(thedates, data[14,[0,1,2,3,4,6,7,8]], 'b')
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=10)
  ax.set_ylabel('Reflectance %')
  

  ax = plt.subplot(2, 1, 2)
  ax.set_title('Coral Brightening in Green')
  ## plt.plot_date(thedates, data[1,0:9], 'g')
  ## plt.plot_date(thedates, data[3,0:9], 'g')
  ## plt.plot_date(thedates, data[5,0:9], 'g')
  ## plt.plot_date(thedates, data[7,0:9], 'g')
  ## plt.plot_date(thedates, data[9,0:9], 'g')
  ## plt.plot_date(thedates, data[11,0:9], 'g')
  ## plt.plot_date(thedates, data[13,0:9], 'g')
  ## plt.plot_date(thedates, data[15,0:9], 'g')
  plt.plot_date(thedates, data[1,[0,1,2,3,4,6,7,8]], 'g')
  plt.plot_date(thedates, data[3,[0,1,2,3,4,6,7,8]], 'g')
  plt.plot_date(thedates, data[5,[0,1,2,3,4,6,7,8]], 'g')
  plt.plot_date(thedates, data[7,[0,1,2,3,4,6,7,8]], 'g')
  plt.plot_date(thedates, data[9,[0,1,2,3,4,6,7,8]], 'g')
  plt.plot_date(thedates, data[11,[0,1,2,3,4,6,7,8]], 'g')
  plt.plot_date(thedates, data[13,[0,1,2,3,4,6,7,8]], 'g')
  plt.plot_date(thedates, data[15,[0,1,2,3,4,6,7,8]], 'g')
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

