#!/bin/env python3
import numpy as np
from matplotlib.dates import (MONTHLY, WEEKLY, DateFormatter, rrulewrapper, RRuleLocator)
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from datetime import date
import sys
import pandas as pd
## from pandas.plotting import register_matplotlib_converters
## register_matplotlib_converters()

infile = "/scratch/dknapp4/Western_Hawaii/Moorea/moorea_sample_coral_output_rb_20190716.csv"
tdata = pd.read_csv(infile)
header = list(tdata)
header.pop(0)
thedates = np.array(tdata['Date'], dtype='S8')
data = np.asarray(tdata[header])
np.save("quick1.npy",data)
np.save("quick2.npy",thedates)
## data = np.load("quick1.npy")
## thedates = np.load("quick2.npy")
thedates = np.asarray([ date(int(day[0:4]), int(day[4:6]), int(day[6:8])) for day in thedates ])

data = data[-9:,:]
thedates = thedates[-9:]
rule = rrulewrapper(MONTHLY, interval=1)
loc = RRuleLocator(rule)
formatter = DateFormatter('%m/%d/%y')

with PdfPages('coral_change_moorea_rb_mean_short_rev20190716.pdf') as pdf:
  ## Page 1, Red
  fig = plt.figure(figsize=(8,10))

  ax = plt.subplot(2, 1, 1)
  ax.set_title('')
  good = np.not_equal(data[:,0], -9.)
  tmean = np.mean(data[good,0:8], axis=1)
  tsdev = np.std(data[good,0:8], axis=1)
  plt.errorbar(thedates[good], tmean, yerr=tsdev, fmt='-bo', capsize=3)
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=10)
  ## plt.plot_date(thedates[good], tmean, 'b')
  ax.set_ylabel('Reflectance')
  
  ax = plt.subplot(2, 1, 2)
  ax.set_title('')
  good = np.not_equal(data[:,8], -9.)
  tmean = np.mean(data[good,8:16], axis=1)
  tsdev = np.std(data[good,8:16], axis=1)
  plt.errorbar(thedates[good], tmean, yerr=tsdev, fmt='-go', capsize=3)
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=10)
  ## plt.plot_date(thedates[good], tmean, 'g')
  ax.set_ylabel('Reflectance')

  pdf.savefig(fig)
  fig.savefig("slide_time_series_mean_rb_short.png", format='png')
  plt.close()

  ## d = pdf.infodict()
  ## d['Title'] = 'Coral Brightening at Moorea (July 2018 - July 2019)'
  ## d['Author'] = 'David Knapp'
  ## d['Subject'] = 'Allen Coral Atlas'
  ## d['CreationDate'] = date(2019, 7, 3)
  ## d['ModDate'] = date.today()

