#!/bin/env python3
import gdal
import numpy as np
import os, sys
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, WEEKLY, DateFormatter, rrulewrapper, WeekdayLocator, RRuleLocator, TU)
from matplotlib.backends.backend_pdf import PdfPages
from datetime import date

## basesamp_num12.npy
datestrings = ['20190813', '20190820', '20190827', '20190903', '20190910', 
'20190917', '20190924', '20191001', '20191008', '20191015', '20191022', 
'20191029', '20191105', '20191112', '20191119'] 

## datestrings = [ os.path.splitext(x)[0][-8:] for x in datanpy ]
thedates = [ date(int(x[0:4]), int(x[4:6]), int(x[6:8])) for x in datestrings ]
rbmeansabove = []
rbsdevsabove = []
## rbmeansbelow = []
## rbsdevsbelow = []
basemeansabove = []
basesdevsabove = []
## basemeansbelow = []
## basesdevsbelow = []

thevals = [2,3,4,5,6,7,8,9,10,11,12,13,14]

basearr = np.zeros((len(thevals), 2))
bigarr = np.zeros((len(datestrings), len(thevals), 2))

for k,numpv in enumerate(thevals):
  basefile = ('basesamp_num%02d.npy'%(numpv))   
  bdata = np.load(basefile)
  basearr[k,0] = np.mean(bdata[0:250])
  basearr[k,1] = np.std(bdata[0:250])
  for j,thisdate in enumerate(datestrings):
    datafile = ('rbsamp_%s_num%02d.npy'%(thisdate,numpv))
    thedata = np.load(datafile)
    bigarr[j,k,0] = np.mean(thedata[0:250])
    bigarr[j,k,1] = np.std(thedata[0:250])

formatter = DateFormatter('%m/%d/%y')
loc = WeekdayLocator(byweekday=TU, interval=1)

with PdfPages('baseline_bleaching_compare_20191126b.pdf') as pdf:
  fig = plt.figure(figsize=(10,8))
  ax = plt.subplot(1, 1, 1)
  ax.set_title('Hawaii Weekly Refl.')
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(formatter)
  ax.xaxis.set_tick_params(rotation=30, labelsize=7)
  plt.errorbar(thedates, np.repeat(basearr[0,0], len(thedates)), yerr=np.repeat(basearr[0,1],len(thedates)), fmt='-', capsize=5, label='Baseline')
  plt.errorbar(thedates, bigarr[:,0,0], yerr=bigarr[:,0,1], fmt='-.b', capsize=5, label='PV 2')
  plt.errorbar(thedates, bigarr[:,1,0], yerr=bigarr[:,1,1], fmt='--b', capsize=5, label='PV 3')
  plt.errorbar(thedates, bigarr[:,2,0], yerr=bigarr[:,2,1], fmt='-b', capsize=5, label='PV 4')
  plt.errorbar(thedates, bigarr[:,3,0], yerr=bigarr[:,3,1], fmt='-.g', capsize=5, label='PV 5')
  plt.errorbar(thedates, bigarr[:,4,0], yerr=bigarr[:,4,1], fmt='--g', capsize=5, label='PV 6')
  plt.errorbar(thedates, bigarr[:,5,0], yerr=bigarr[:,5,1], fmt='-g', capsize=5, label='PV 7')
  plt.errorbar(thedates, bigarr[:,6,0], yerr=bigarr[:,6,1], fmt='-.r', capsize=5, label='PV 8')
  plt.errorbar(thedates, bigarr[:,7,0], yerr=bigarr[:,7,1], fmt='--r', capsize=5, label='PV 9')
  plt.errorbar(thedates, bigarr[:,8,0], yerr=bigarr[:,8,1], fmt='-r', capsize=5, label='PV 10')
  plt.errorbar(thedates, bigarr[:,9,0], yerr=bigarr[:,9,1], fmt='-r', lw=2, capsize=5, label='PV 11')
  plt.errorbar(thedates, bigarr[:,10,0], yerr=bigarr[:,10,1], fmt='-r', lw=3, capsize=5, label='PV 12')
  plt.errorbar(thedates, bigarr[:,11,0], yerr=bigarr[:,11,1], fmt='-.r', lw=3, capsize=5, label='PV 13')
  plt.errorbar(thedates, bigarr[:,12,0], yerr=bigarr[:,12,1], fmt='-.r', lw=4, capsize=5, label='PV 14')
  plt.legend(loc='lower right')
  pdf.savefig(fig)

plt.close()
