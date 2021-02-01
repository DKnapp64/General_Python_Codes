#!/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, WEEKLY, DateFormatter, rrulewrapper, RRuleLocator)
from matplotlib.backends.backend_pdf import PdfPages
from datetime import date
import sys

data = np.genfromtxt("/scratch/dknapp4/Western_Hawaii/Moorea/moorea_sample_coral_output_rb_20190716.csv", 
  dtype=[('date', 'S8'), ('b1', float), ('b2', float), ('b3', float),
  ('b4', float), ('b5', float), ('b6', float), ('b7', float), ('b8', float),
  ('g1', float), ('g2', float), ('g3', float), ('g4', float), ('g5', float), 
  ('g6', float), ('g7', float), ('g8', float), ('b1sd', float), ('b2sd', float), 
  ('b3sd', float), ('b4sd', float), ('b5sd', float), ('b6sd', float), ('b7sd', float),
  ('b8sd', float), ('g1sd', float), ('g2sd', float), ('g3sd', float), ('g4sd', float),
  ('g5sd', float), ('g6sd', float), ('g7sd', float), ('g8sd', float)], skip_header=1, delimiter=',')

thedates = []

for thisdate in data:
  yr = int(thisdate[0][0:4])
  month = int(thisdate[0][4:6])
  day = int(thisdate[0][6:])
  thedates.append(date(yr, month, day))

thedates = np.asarray(thedates)

rule = rrulewrapper(WEEKLY, interval=1)
loc = RRuleLocator(rule)
formatter = DateFormatter('%m/%d/%y')

thedates = thedates[-7:]
data = data[-7:]

with PdfPages('coral_change_moorea_rb_short_rev20190811.pdf') as pdf:
  ## Page 1, Red
  fig = plt.figure(figsize=(8,10))

  ax = plt.subplot(2, 1, 1)
  ax.set_title('')
  for samp in range(1,9):
    bname = 'b'+("%1d" % samp)
    temp = data[bname]
    good = np.not_equal(temp, -9.)
    plt.plot_date(thedates[good], temp[good], 'b')
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=10)
  ax.set_ylabel('Bottom Reflectance')
  
  ax = plt.subplot(2, 1, 2)
  ax.set_title('')
  for samp in range(9,17):
    bname = 'g'+('%1d' % (samp-8))
    temp = data[bname]
    good = np.not_equal(temp, -9.)
    plt.plot_date(thedates[good], temp[good], 'g')
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=10)
  ax.set_ylabel('Reflectance')
  pdf.savefig(fig)
  fig.savefig("slide_time_series_short_rb.png", format='png')
  plt.close()

  ## d = pdf.infodict()
  ## d['Title'] = 'Coral Brightening at Moorea (July 2018 - July 2019)'
  ## d['Author'] = 'David Knapp'
  ## d['Subject'] = 'Allen Coral Atlas'
  ## d['CreationDate'] = date(2019, 7, 3)
  ## d['ModDate'] = date.today()

