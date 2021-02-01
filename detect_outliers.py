import os
import numpy as np
from sklearn.ensemble import IsolationForest
import re
from numpy.lib.recfunctions import append_fields
from spectral import *

## import pdb
## import matplotlib.pyplot as plt

## infile = 'peru_spectral_lib_filtered_20170317.csv'
## infile = 'peru_vswir_extraction_20170319.csv'
infile = 'peru_vswir_extraction_20170324.csv'

## figure out what the longest string is among the variable-length text columns (usecols),
## then build the data type format string to read all of the data.
junk = np.genfromtxt(infile, delimiter=',', skip_header=4, usecols=[0,2,3,4,5,6,7,8,9,10], dtype='S')
tempdtype = "S%d,i8,S%d,S%d,S%d,S%d,S%d,S%d,S%d,S%d,S%d,S9,S9,i8,S20,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,(214)f8"
dtypestr = (tempdtype) % tuple(np.ones(10) * junk.dtype.itemsize)
indata = np.genfromtxt(infile, delimiter=',', skip_header=3, names=True, dtype=dtypestr, autostrip=True)

## indata = np.load('peru_spectral_lib_filtered_20170324.npy')

## band bands list as 1-based, but convertted to 0-based (i.e., subtracting 1)
badbands = np.array([1,2,3,4,5,6,7,8,9,100,101,102,103,104,105,106,107, \
            108,109,110,111,112,113,144,145,146,147,148,149,150, \
            151,152,153,154,155,156,157,158,159,160,161,162,163, \
            164,165,166,167,168,169,213,214]) - 1 

goodbands = [m for m in np.arange(0,214) if m not in badbands]

## set all badbands to zero?
indata['Band_1'][:,badbands] = 0

## Find the spectra that have a zero in the good bands region

## RUN VARIOUS TESTS TO SEE WHICH RECORDS (SPECTRA) SHOULD BE REMOVED
#
## which have bands with zeros in the good band regions?
nogoodbandszero = ~(np.any(indata['Band_1'][:,goodbands] == 0, axis=1))
## pdb.set_trace()

## which are records from single pixels (i.e., no mean or stdev records)?
singlepix = (indata['MeanStdev'] == 'pixel')
## which are records from separate flight lines (i.e., start with "CAO")?
cao = [os.path.basename(b)[0:3] == 'CAO' for b in indata['Reflectance_file'].tolist()]
## these next 4 lines reassign the Sensor type based on being CAO and the year.
cao11 = [os.path.basename(b)[0:7] == 'CAO2011' for b in indata['Reflectance_file'].tolist()]
cao12 = [os.path.basename(b)[0:7] == 'CAO2012' for b in indata['Reflectance_file'].tolist()]
cao13 = [os.path.basename(b)[0:7] == 'CAO2013' for b in indata['Reflectance_file'].tolist()]
indata['Sensor'][cao11] = 'vswir2'
indata['Sensor'][cao12] = 'vswir2'
indata['Sensor'][cao13] = 'vswir3'
## yearcao = np.asarray([int(os.path.basename(b)[3:7]) for b in indata[cao]['Reflectance_file']])
## which spectra are not from BRDF corrected data?
nofindbrdf = re.compile('brdf')
notbrdf = [nofindbrdf.search(os.path.basename(b)) is None for b in indata['Reflectance_file'].tolist()]
brdfcolumn = np.empty(len(indata), dtype='S7')
brdfcolumn[:] = ''
brdfcolumn[notbrdf] = 'no'
brdf = [not i for i in notbrdf]
brdfcolumn[brdf] = 'yes'

np.save('peru_spectral_lib_unfiltered_20170403.npy', indata)

#u put those boolean vectors together to look across for all "True"s
## trutharray = np.vstack((nogoodbandszero, singlepix, cao, notbrdf)).T
trutharray13 = np.vstack((nogoodbandszero, singlepix, cao13)).T
allgood13 = np.all(trutharray13, axis=1)

## create a data structure of the records that pass all of those tests for 2013
filtdata = indata[allgood13]
brdfcolumngood = brdfcolumn[allgood13]

brightnessgood = [np.sqrt(sum(pow(bright[goodbands],2))) > 20000 for bright in filtdata['Band_1']]
ndvigood = [(spec[45]-spec[33])/(spec[45]+spec[33]) >= 0.8 for spec in filtdata['Band_1']]
trutharray2 = np.vstack((brightnessgood, ndvigood)).T
allgood2 = np.all(trutharray2, axis=1)
filtdata2 = filtdata[allgood2]
brdfcolumngood2  = brdfcolumngood[allgood2]
np.save('peru_spectral_lib_filtered_2013_20170403.npy', filtdata2)
np.save('peru_brdfcolumngood_2013_20170403.npy', brdfcolumngood2)
filtdata2['Band_1'].tofile('peru_filt2_2013_20170403_binary')

## create a data structure of the records that pass all of those tests for 2012
## trutharray12 = np.vstack((nogoodbandszero, singlepix, cao12)).T
## allgood12 = np.all(trutharray12, axis=1)
## filtdata = indata[allgood12]
## brdfcolumngood = brdfcolumn[allgood12]
## 
## brightnessgood = [np.sqrt(sum(pow(bright[goodbands],2))) > 20000 for bright in filtdata['Band_1']]
## ndvigood = [(spec[45]-spec[33])/(spec[45]+spec[33]) >= 0.8 for spec in filtdata['Band_1']]
## trutharray2 = np.vstack((brightnessgood, ndvigood)).T
## allgood2 = np.all(trutharray2, axis=1)
## filtdata2 = filtdata[allgood2]
## brdfcolumngood2  = brdfcolumngood[allgood2]
## np.save('peru_spectral_lib_filtered_2012_20170403.npy', filtdata2)
## np.save('peru_brdfcolumngood_2012_20170403.npy', brdfcolumngood2)
## filtdata2['Band_1'].tofile('peru_filt2_2012_20170403_binary')
## 
## ## create a data structure of the records that pass all of those tests for 2011
## trutharray11 = np.vstack((nogoodbandszero, singlepix, cao11)).T
## allgood11 = np.all(trutharray11, axis=1)
## filtdata = indata[allgood11]
## brdfcolumngood = brdfcolumn[allgood11]
## 
## brightnessgood = [np.sqrt(sum(pow(bright[goodbands],2))) > 20000 for bright in filtdata['Band_1']]
## ndvigood = [(spec[45]-spec[33])/(spec[45]+spec[33]) >= 0.8 for spec in filtdata['Band_1']]
## trutharray2 = np.vstack((brightnessgood, ndvigood)).T
## allgood2 = np.all(trutharray2, axis=1)
## filtdata2 = filtdata[allgood2]
## brdfcolumngood2  = brdfcolumngood[allgood2]
## np.save('peru_spectral_lib_filtered_2011_20170403.npy', filtdata2)
## np.save('peru_brdfcolumngood_2011_20170403.npy', brdfcolumngood2)
## filtdata2['Band_1'].tofile('peru_filt2_2011_20170403_binary')
## 

## fix the sensor information based on date
year = [int(os.path.basename(b)[3:7]) for b in filtdata['Reflectance_file'].tolist()]
## 
## random sample
## pdb.set_trace()
## training_sample = np.random.random_integers(0, len(filtdata2), size=np.int(np.floor(0.01*len(filtdata2))))
## testing_sample = [m for m in np.arange(0,len(filtdata2)) if m not in training_sample]

## training_sample = np.array([5,15,32,41,51,57,24,12,28468,28474,28484,28492,28497,28460,28449,28443,29486,28452,28444,29753, \
##   29762,29769,27277,27273,27269,27266,27263,27259,27256,27255,27253,27251,32890,32895,32900,32904,32910,35964,35966,35954, \
##   35949,35944,35938,35930,35953,65248,65245,65241,65234,65230,65227,65223,65219,65217,65209,65204,65201,65237,65248,65250, \
##   65253,65255,13264,13268,13257,13252,13249,13245,10625,10629]) - 1
## 
## ## subset data for training and testing

## I have found mask arrays to be buggy when used on complicated data structures like this, so use them with caution.
## Better yet, don't use them and make an "opposite" index to split up data into training and testing sets as shown above.
## temp = np.ma.array(filtdata2, mask=False)
## temp.mask[training_sample] = True
## X_test = np.ma.compress_rows(temp)
## X_train = filtdata2[training_sample]['Band_1']
## X_test = filtdata2[testing_sample]['Band_1']

## append the BRDF column
filtdata2b = append_fields(filtdata2, 'BRDF', brdfcolumngood2)

## Train it with all of the data
X_train = filtdata2['Band_1']

clf = IsolationForest(max_samples="auto")

print "Starting Isoaltion Forest"
clf.fit(X_train)
y_pred_train = clf.predict(X_train)
## y_pred_test = clf.predict(X_test)

odd_data = X_train[y_pred_train == -1,:]
odd_data_names = filtdata2[y_pred_train == -1]["CSP_CODE"]
good_data = X_train[y_pred_train == 1,:]         
good_data_names = filtdata2[y_pred_train == 1]["CSP_CODE"]
np.savetxt('peru_anomalies_20170403.csv', odd_data, delimiter=',')
np.savetxt('peru_nonanomalies_20170403.csv', good_data, delimiter=',')                   
odd_data.tofile('peru_anomalies_20170403_binary')
good_data.tofile('peru_nonanomalies_20170403_binary')   

bandstuff = np.genfromtxt('vswir3_wv_fwhm.txt')

meta = {}
meta['file type'] = 'ENVI Spectral Library'
meta['samples'] = odd_data.shape[1]
meta['lines'] = odd_data.shape[0]
meta['bands'] = 1
meta['header offset'] = 0
meta['data type'] = 5           # 32-bit float
meta['interleave'] = 'bsq'
meta['byte order'] = 0
meta['wavelength units'] = 'Nanometers'
meta['spectra names'] = [str(n) for n in odd_data_names]
meta['wavelength'] = bandstuff[:,0]
meta['fwhm'] = bandstuff[:,1]
envi.write_envi_header('peru_anomalies_20170403_binary.hdr', meta, True)
