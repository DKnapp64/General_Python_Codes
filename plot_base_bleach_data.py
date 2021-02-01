#!/bin/env python3
import gdal
import numpy as np
import os, sys
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, WEEKLY, DateFormatter, rrulewrapper, WeekdayLocator, RRuleLocator, TU)
from matplotlib.backends.backend_pdf import PdfPages
from datetime import date

datanpz = ['bleach_data_extracted_20190813.npz', 
'bleach_data_extracted_20190820.npz', 
'bleach_data_extracted_20190827.npz', 
'bleach_data_extracted_20190903.npz', 
'bleach_data_extracted_20190910.npz', 
'bleach_data_extracted_20190917.npz', 
'bleach_data_extracted_20190924.npz', 
'bleach_data_extracted_20191001.npz', 
'bleach_data_extracted_20191008.npz', 
'bleach_data_extracted_20191015.npz', 
'bleach_data_extracted_20191022.npz', 
'bleach_data_extracted_20191029.npz', 
'bleach_data_extracted_20191105.npz', 
'bleach_data_extracted_20191112.npz', 
'bleach_data_extracted_20191119.npz']

datestrings = [ os.path.splitext(x)[0][-8:] for x in datanpz ]
thedates = [ date(int(x[0:4]), int(x[4:6]), int(x[6:8])) for x in datestrings ]
rbmeansabove = []
rbsdevsabove = []
rbmeansbelow = []
rbsdevsbelow = []
basemeansabove = []
basesdevsabove = []
basemeansbelow = []
basesdevsbelow = []

for j,thisdate in enumerate(datestrings):
  datafile = 'bleach_data_extracted_'+thisdate+'.npz'   
  npz = np.load(datafile)
  rbmeansabove.append(np.mean(npz['rabove']))
  rbsdevsabove.append(np.std(npz['rabove']))
  rbmeansbelow.append(np.mean(npz['rbelow']))
  rbsdevsbelow.append(np.std(npz['rbelow']))

  basemeansabove.append(np.mean(npz['baseabove']))
  basesdevsabove.append(np.std(npz['baseabove']))
  basemeansbelow.append(np.mean(npz['basebelow']))
  basesdevsbelow.append(np.std(npz['basebelow']))

## rule = rrulewrapper(WEEKLY, byweekday=TU, interval=1)
## loc = RRuleLocator(rule)
formatter = DateFormatter('%m/%d/%y')
loc = WeekdayLocator(byweekday=TU, interval=1)

with PdfPages('baseline_bleaching_compare_20191122.pdf') as pdf:
  fig = plt.figure(figsize=(10,8))
  ax = plt.subplot(2, 1, 1)
  ax.set_title('Hawaii Baseline Refl.')
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=7)
  plt.errorbar(thedates, np.asarray(basemeansabove), yerr=np.asarray(basesdevsabove), fmt='--r', capsize=5, label='Baseline Bleach Det.' )
  plt.errorbar(thedates, np.asarray(basemeansbelow), yerr=np.asarray(basesdevsbelow), fmt='--b', capsize=5, label='Baseline No Bleach Det.')
  plt.legend(loc='lower right')
  ax = plt.subplot(2, 1, 2)
  ax.set_title('Hawaii Weekly Bleaching Refl.')
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=7)
  plt.errorbar(thedates, np.asarray(rbmeansabove), yerr=np.asarray(rbsdevsabove), fmt='-r', capsize=5, label='High Temp. Bleach Det.')
  plt.errorbar(thedates, np.asarray(rbmeansbelow), yerr=np.asarray(rbsdevsbelow), fmt='-b', capsize=5, label='High Temp. No Bleach Det.')
  plt.legend(loc='lower right')
  pdf.savefig(fig)
  plt.close()

plt.close()
