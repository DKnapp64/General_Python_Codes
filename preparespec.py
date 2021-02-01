#!/usr/bin/env python2
import os, sys
import numpy as np
from sklearn.ensemble import IsolationForest
import re
from numpy.lib.recfunctions import append_fields
import string
from spectral import *
import shapefile as shp
import pandas as pd
import osgeo.osr
## import osr
import warnings


def main(masterspecfile, masterchemfile, mergedfile, output_shapefile, utmzone):

  warnings.filterwarnings("ignore")

  ## masterspecfile = 'sabah_master_vswir_extraction_20170530.csv'

  ## figure out what the longest string is among the variable-length text columns (usecols),
  ## then build the data type format string to read all of the data.
  junk = np.genfromtxt(masterspecfile, delimiter=',', skip_header=4, usecols=[0,2,3,4,5,6,7,8,9,10], dtype='S')
  
  tempdtype = "S%d,i8,S%d,S%d,S%d,S%d,S%d,S%d,S%d,S%d,S%d,S9,S9,S9,i8,S20,S8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,(214)f8"
  dtypestr = (tempdtype) % tuple(np.ones(10) * junk.dtype.itemsize)
  indata = np.genfromtxt(masterspecfile, delimiter=',', skip_header=3, names=True, dtype=dtypestr, autostrip=True)
  
  ## Bad Bands as provided to me from Dana Chadwick from email on 26-May-2017
  badbands = np.array([1,2,3,4,5,6,7,8,9,100,101,102,103,104,105,106,107, \
              108,109,110,111,112,113,144,145,146,147,148,149,150, \
              151,152,153,154,155,156,157,158,159,160,161,162,163, \
              164,165,166,167,168,169,211,212,213,214]) - 1 
  
  goodbands = [m for m in np.arange(0,214) if m not in badbands]
  
  ## which are records from single pixels (i.e., no mean or stdev records)?
  singlepix = (indata['MeanStdev'] == 'pixel')
  
  ## which are records from separate flight lines (i.e., start with "CAO")?
  cao = [os.path.basename(b)[0:3] == 'CAO' for b in indata['Reflectance_file'].tolist()]
  
  ## cao16 = [os.path.basename(b)[0:7] == 'CAO2016' for b in indata['Reflectance_file'].tolist()]
  ## indata['Sensor'][cao16] = 'vswir3'
   
  ## np.save('sabah_spectral_lib_unfiltered_20170530.npy', indata)
  
  ## create a data structure of the records that pass all of those tests
  ## filtdata = indata[allgood]
  filtdata = indata
  
  brightness = [np.sqrt(sum(pow(bright[goodbands],2))) for bright in filtdata['Band_1']]
  ndvi = [(spec[45]-spec[33])/(spec[45]+spec[33]) for spec in filtdata['Band_1']]
  
  ## np.save('sabah_spectral_lib_filtered_20170530.npy', filtdata)
  ## filtdata['Band_1'].tofile('sabah_filt_20170530_binary')
  
  ## Train it with all of the data
  X_train = filtdata['Band_1']
  
  clf = IsolationForest(max_samples="auto")
  
  print "Starting Isolation Forest for Anomaly Detection"
  clf.fit(X_train)
  y_pred_train = clf.predict(X_train)
  
  ## append the Brightness, NDVI, and Anomaly columns
  filtdata2 = append_fields(filtdata, names=('Brightness', 'NDVI', 'AnomScore'), data=(brightness, ndvi, clf.decision_function(X_train)))
  
  ## X_train.tofile('sabah_user_spectral_20170530_binary')   
  
  good_data_names = filtdata2['CSP_CODE']
  
  bandstuff = np.genfromtxt('../Peru_CSP_Extract/vswir3_wv_fwhm.txt')
  
  ##  OK, some things in python and numpy can ridiculously restrictive, 
  ## so the following is my way of getting around it.  
  ## First break up the text variables that we want to keep
  ## finaltext = finalgood[['CSP_CODE', 'PixelID', 'Reflectance_file', 'BRDF']].copy()
  finaltext = filtdata2[['CSP_CODE', 'PixelID', 'Reflectance_file', 'MaskedPix', 'Res']].copy()
  ## Second break up the spectral variables
  finalspec = filtdata2['Band_1'].copy()
  finaltests = filtdata2[['Brightness', 'NDVI', 'AnomScore']].copy()
  ## Third, stack the data, reshaping the single-columns so that they will stack correctly
  ## (to get around strange limitation of hstack).
  goodlen = len(good_data_names)
  reflbases = [os.path.basename(nameit) for nameit in filtdata2['Reflectance_file']]
  finaltext['Reflectance_file'] = reflbases
  
  finalfinal = np.hstack((finaltext['CSP_CODE'].reshape((goodlen,1)), finaltext['PixelID'].reshape((goodlen,1)), \
    finaltext['Reflectance_file'].reshape((goodlen,1)), finaltext['MaskedPix'].reshape((goodlen,1)), \
    finaltext['Res'].reshape((goodlen,1)), finaltests['Brightness'].reshape((goodlen,1)), \
    finaltests['NDVI'].reshape((goodlen,1)), finaltests['AnomScore'].reshape((goodlen,1)), finalspec))
  temphdr = str.replace(str(finaltext.dtype.names).strip("()"), "'", "")
  
  bandstring = ['Band_'+d for d in map(str,np.arange(214)+1)] 
  temp1 = str.replace(str(bandstring),"[",'')
  temp2 = str.replace(temp1,"]",'')
  temp3 = str.replace(temp2,"'",'')
  finalheader = temphdr + ',' + str.replace(str(finaltests.dtype.names).strip("()"), "'", "") + ',' + temp3
  
  np.savetxt('temp_spec_file.csv', finalfinal, delimiter=',', header=finalheader, fmt='%s', comments='')
  

  ## Write out ENVI Spectral library header file
  meta = {}
  meta['file type'] = 'ENVI Spectral Library'
  meta['samples'] = X_train.shape[1]
  meta['lines'] = X_train.shape[0]
  meta['bands'] = 1
  meta['header offset'] = 0
  meta['data type'] = 5           # 64-bit float
  meta['interleave'] = 'bsq'
  meta['byte order'] = 0
  meta['wavelength units'] = 'Nanometers'
  meta['spectra names'] = [str(n) for n in good_data_names]
  meta['wavelength'] = bandstuff[:,0]
  meta['fwhm'] = bandstuff[:,1]
  ## envi.write_envi_header('sabah_user_spectral_20170530_binary.hdr', meta, True)

  dfspec = pd.read_csv('temp_spec_file.csv', skipinitialspace=True)
  dfchem = pd.read_csv(masterchemfile, skipinitialspace=True, na_values=["-999","-999.0",""])

  good = np.logical_and(np.greater(dfspec['NDVI'], 0.5), np.equal(dfspec['MaskedPix'], 'good'))
  dfspec = dfspec[good]

  chemcols = ['CODE', 'LMA', 'Water', 'Chl-a', 'Chl-b', 'Car', 'Phenols', 'Tannins', 'N', 'C', 'P', 'Ca', \
              'K', 'Mg', 'B', 'Fe', 'Mn', 'Zn', 'Al', 'Cu', 'S', 'Delta-15N', 'Delta-13C', 'Soluble-C', \
              'Hemi-cellulose', 'Cellulose', 'Lignin', 'Ash', 'Chl_AnB', 'NtoP']

  # Reduce the chem data to just hte chem columns of interest
  dfchem = dfchem[chemcols]
  
  # Set any remaining low values to NaN.
  for i in range(1, dfchem.shape[1]):
    lowval = np.less(dfchem[chemcols[i]], -900)
    dfchem[chemcols[i]][lowval] = np.nan
  
  # Merge the spectra and chem data using the CSP_CODE
  dfmerged = pd.merge(left=dfspec, right=dfchem, left_on='CSP_CODE', right_on='CODE')
  
  # make an array of hte column names for possible future use
  headerspec = list(dfspec)

  uniqcsp = np.unique(dfmerged['CSP_CODE'])

  np.random.seed(13)

  randint = np.floor(np.random.random(np.floor(len(uniqcsp) * 0.7).astype(int)) * len(uniqcsp)).astype(int)
  cal = np.zeros(len(uniqcsp), dtype=bool)
  cal[:] = False
 
  for value in randint:
    cal[value] = True

  ## set similar boolean array to be the complement (opposite) for the validation set
  val = np.logical_not(cal)

  ## create arrays of the set of CSPs for calibration and validation
  calcsp = uniqcsp[cal]
  valcsp = uniqcsp[val]
  
  ## create boolean array for the selection of spectra/chem calibration records from the merged array
  calrecs = np.zeros(len(dfmerged), dtype=bool)
  
  calval = np.zeros(len(dfmerged), dtype=int)
  
  ## Set spectral/chem record to True for calibration if it is among the CSPs selected for calibration,
  ## False otherwise
  for i,recs in enumerate(dfmerged['CSP_CODE']):
    if (recs in calcsp):
      calrecs[i] = True
      calval[i] = 1
    else:
      calrecs[i] = False
      calval[i] = 0
  
  ## create the complement (opposite) boolean array for the validation records
  ## valrecs = np.logical_not(calrecs)
  
  dfmerged['CalVal'] = calval
  dfmerged.to_csv(mergedfile)

  print "Finished Saving Merged Spec/Chem File"
  
  dtypestr = "S9,S20,S50,S7,f8,f8,f8,f8,(214)f8"
  indata = np.genfromtxt('temp_spec_file.csv', delimiter=',', names=True, dtype=dtypestr, autostrip=True)
  x,y,cspcode,pixid,reflfile,masked,bright,ndvi,anomscore = [],[],[],[],[],[],[],[],[]
  numpixs = len(indata)

  for row in indata:
    ## parse coords
    xval = float(row['PixelID'][1:9])/100. + (0.5 * float(row['Res']))
    yval = float(row['PixelID'][10:])/100. - (0.5 * float(row['Res']))

    pixid.append(row['PixelID'])
    cspcode.append(row['CSP_CODE'])
    reflfile.append(row['Reflectance_file'])
    masked.append(row['MaskedPix'])
    bright.append(float(row['Brightness']))
    ndvi.append(float(row['NDVI']))
    anomscore.append(float(row['AnomScore']))
    x.append(xval)
    y.append(yval)

  #Set up shapefile writer and create empty fields
  w = shp.Writer(shp.POINT)
  w.autoBalance = 1 #ensures geometry and attributes match
  w.field('CSP_CODE','C',9)
  w.field('PIXID','C',20)
  w.field('Reflfile','C',40)
  w.field('MaskPix','C', 9)
  w.field('Bright','N', 13, 1)
  w.field('NDVI','N', 14, 5)
  w.field('ANOMSCR','N', 18, 4)

  #loop through the data and write the shapefile
  for j,k in enumerate(x):
    w.point(k, y[j]) #write the geometry
    w.record(cspcode[j], pixid[j], reflfile[j], masked[j], bright[j], ndvi[j], anomscore[j]) #write the attributes

  #Save shapefile
  w.save(output_shapefile)

  ## Create PRJ file to go along with Shapefile
  spatial_ref = osr.SpatialReference()

  if int(sys.argv[5]) > 0:
    epsgval = 32600 + int(sys.argv[5])
  else:
    epsgval = 32700 + abs(int(sys.argv[5]))

  spatial_ref.ImportFromEPSG(epsgval)
  spatial_ref.MorphToESRI()          
  wkt_epsg = spatial_ref.ExportToWkt()           

  prjname = os.path.splitext(output_shapefile)[0]+'.prj'

  with open(prjname, "w") as prj:
    prj.write(wkt_epsg)

  print "Finished Saving OUtput Shapefile of Spectra Locations"

  
if __name__ == "__main__":
  
 if len( sys.argv ) != 6:
    print "[ USAGE ] you must supply 5 arguments: master_spec_extraction master_chem out_merged_csv output_shapefile utmzone"
    print "example : preparespec.py master_spec_extraction master_chem out_merged_csv output_shapefile utmzone"
    print ""
    sys.exit( 1 )

 print main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] )
