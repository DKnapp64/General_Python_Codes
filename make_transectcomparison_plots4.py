#!/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import os, sys
import depth_rb_single_special

csvfile = '/scratch/dknapp4/ASD/Spectroscopy/Moorea_dove_rb_sr_transects_20190710.csv'

## D2T100007, 2019-06-04T21:22:11Z,   2,  0.2646,  0.2954,  0.3194,  0.0091,  0.0263,  0.0487,   13.63,  0.1237,  0.0910, -0.3668,  0.0499,  0.0373,  0.0111,  0.0116

data = np.genfromtxt(csvfile, delimiter=',', autostrip=True, dtype=[('ASDName', 'S9'), ('DateTime', 'S20'), ('numvals', 'i8'), ('basdm', 'f8'), 
  ('gasdm', 'f8'), ('rasdm', 'f8'), ('basdsd', 'f8'), ('gasdsd', 'f8'), ('rasdsd', 'f8'), ('depth', 'f8'), ('brb', 'f8'), 
  ('grb', 'f8'), ('rrb', 'f8'), ('bsr', 'f8'), ('gsr', 'f8'), ('rsr', 'f8'), ('nsr', 'f8')], skip_header=1)

## quints = np.percentile(data['depth'], [0,20,40,60,80,100])

## plt.errorbar(data['GreenASD'], data['GreenRb'], xerr=data['GreenASDSDev'], yerr=data['GreenRbSDev'], fmt='o')
## thesam = [0.4, 0.6, 0.8, 1.0]

## Get unique transects
untrans = np.unique([ trans[0:4] for trans in data['ASDName'] ])   
## untrans = untrans[[7,10]]

with PdfPages('Moorea_transects_ASD_vs_Dove_transcompare_rev20190716.pdf') as pdf:
  ## Page 1
  for d,thetrans in enumerate(untrans):
    print(thetrans)
    index = np.flatnonzero(np.core.defchararray.find(data['ASDName'], thetrans) != -1)

    ## transdata = data[['basdm','brb','gasdm','grb', 'basdsd', 'gasdsd', 'depth']][index]
    transdata = data[['basdm','brb','gasdm','grb', 'basdsd', 'gasdsd', 'depth', 'bsr', 'gsr', 'rsr', 'nsr']][index]
    ## dindex1 = np.less_equal(transdata['depth'], quints[1])
    ## dindex2 = np.logical_and(np.less_equal(transdata['depth'], quints[2]), np.greater(transdata['depth'], quints[1]))
    ## dindex3 = np.logical_and(np.less_equal(transdata['depth'], quints[3]), np.greater(transdata['depth'], quints[2]))
    ## dindex4 = np.logical_and(np.less_equal(transdata['depth'], quints[4]), np.greater(transdata['depth'], quints[3]))
    ## dindex5 = np.greater_equal(transdata['depth'], quints[4])
    ## syms = np.zeros(transdata.shape[0], dtype='S7')
    ## syms[dindex1] = '#011b56'
    ## syms[dindex2] = '#0269a4'
    ## syms[dindex3] = '#00b4ab'
    ## syms[dindex4] = '#ffd832'
    ## syms[dindex5] = '#fe7c00'
    ## syms = syms.tolist()
    ## syms = [ dec.decode() for dec in syms ]

    newarr = np.zeros((transdata.shape[0], 10), dtype=np.float32)
    for k in np.arange(transdata.shape[0]):
      vals = depth_rb_single_special.depth_rb_single(transdata['bsr'][k], transdata['gsr'][k], transdata['rsr'][k], transdata['nsr'][k], 0.5)
      newarr[k,0] = vals[0] 
      newarr[k,1] = vals[1] 
      vals = depth_rb_single_special.depth_rb_single(transdata['bsr'][k], transdata['gsr'][k], transdata['rsr'][k], transdata['nsr'][k], 0.6)
      newarr[k,2] = vals[0] 
      newarr[k,3] = vals[1] 
      vals = depth_rb_single_special.depth_rb_single(transdata['bsr'][k], transdata['gsr'][k], transdata['rsr'][k], transdata['nsr'][k], 0.7)
      newarr[k,4] = vals[0] 
      newarr[k,5] = vals[1] 
      vals = depth_rb_single_special.depth_rb_single(transdata['bsr'][k], transdata['gsr'][k], transdata['rsr'][k], transdata['nsr'][k], 0.8)
      newarr[k,6] = vals[0] 
      newarr[k,7] = vals[1] 
      vals = depth_rb_single_special.depth_rb_single(transdata['bsr'][k], transdata['gsr'][k], transdata['rsr'][k], transdata['nsr'][k], 0.9)
      newarr[k,8] = vals[0] 
      newarr[k,9] = vals[1] 
    
    fig = plt.figure(figsize=(8,10))

    ax1 = plt.subplot(2, 1, 1)
    ax1.set_title(thetrans.decode() + ' Blue Band')
    ax1.set_xlabel('Distance/Time along Transect')
    ax1.set_ylabel('Bottom Reflectance')
    ## plt.plot(transdata['brb'], transdata['basdm'], '-b', label="Rb Dove")
    plt.plot(transdata['basdm'], '-b', label="ASD")
    ## plt.scatter(np.arange(transdata['basdm'].shape[0]),transdata['basdm'], c=syms, label="ASD Means")
    plt.plot(transdata['brb'], '-k', label="Rb")     
    ## plt.plot(newarr[:,0], '--k', label="Rb (Chla=0.5)")
    ## plt.plot(newarr[:,2], '-.k', label="Rb (Chla=0.6)")
    ## plt.plot(newarr[:,4], ':k', label="Rb (Chla=0.7)")
    ## plt.plot(newarr[:,6], '--', color='gray', label="Rb (Chla=0.8)")
    ## plt.plot(newarr[:,8], '-.', color='gray', label="Rb (Chla=0.9)")
    ax1.legend()

    ax2 = plt.subplot(2, 1, 2)
    ax2.set_title(thetrans.decode() + ' Green Band')
    ax2.set_xlabel('Distance/Time along Transect')
    ax2.set_ylabel('Bottom Reflectance')
    ## plt.plot(transdata['grb'], transdata['gasdm'], '-g', label="Rb Dove")
    plt.plot(transdata['gasdm'], '-g', label="ASD")
    ## plt.scatter(np.arange(transdata['gasdm'].shape[0]),transdata['gasdm'], c=syms, label="ASD Means")
    plt.plot(transdata['grb'], '-k', label="Rb")     
    ## plt.plot(newarr[:,1], '--k', label="Rb (Chla=0.5)")
    ## plt.plot(newarr[:,3], '-.k', label="Rb (Chla=0.6)")
    ## plt.plot(newarr[:,5], ':k', label="Rb (Chla=0.7)")
    ## plt.plot(newarr[:,7], '--', color='gray', label="Rb (Chla=0.8)")
    ## plt.plot(newarr[:,9], '-.', color='gray', label="Rb (Chla=0.9)")
    ax2.legend()
    fig.savefig('slidepixels'+str(d+1)+'.png', format='png')
    pdf.savefig(fig)

  d = pdf.infodict()
  d['Title'] = 'Moorea Transects ASD vs Dove'
  d['Author'] = 'David Knapp'
  d['Subject'] = 'Allen Coral Atlas'
  d['CreationDate'] = datetime.datetime(2019, 7, 9)
  d['ModDate'] = datetime.datetime.today()


plt.close()
