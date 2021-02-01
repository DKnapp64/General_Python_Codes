import pandas as pd
import numpy as np

csvspecfile = '/Volumes/DGE/Data/Shared/Labs/Asner/Private/Research/Asia/Sabah/PLSR_Work/sabah_user_spectral_data_20170530.csv'
csvchemfile = '/Volumes/DGE/Data/Shared/Projects/CAO/Sabah/CSP_Plot_Setup/a_sabah_leaf_chemistry/Sabah_Leaf_Chemistry_Final.csv'
csvoutfile = 'sabah_user_spectral_chem_merged_20170601b.csv'
## calcsvoutfile = 'sabah_user_spectral_calibration_chem_merged_20170530.csv'
## valcsvoutfile = 'sabah_user_spectral_validation_chem_merged_20170530.csv'

## Read in separate CSVSs of spectra and chems
dfspec = pd.read_csv(csvspecfile, skipinitialspace=True)
dfchem = pd.read_csv(csvchemfile, skipinitialspace=True, na_values=["-999","-999.0",""])

## dropcol = ['PixelID', 'Reflectance_file', 'MaskedPix', 'Brightness', 'NDVI', 'AnomScore']
## for name in dropcol:
##   dfspec = dfspec.drop(name,1)

## filter out spectra with NDVI < 0.5 or with MaskedPix not set to "good".
## good = np.logical_and(np.greater(dfspec['NDVI'], 0.5), np.equal(dfspec['MaskedPix'], 'good'))
## dfspec = dfspec[good]

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
## dfspec = np.array(dfspec)

## find unique CSPs in the merged data
uniqcsp = np.unique(dfmerged['CSP_CODE'])

np.random.seed(13)

# create a random set of indices for half of the data to identify calibration set
randvals = np.random.choice(len(uniqcsp)-1, int(np.floor(len(uniqcsp) * 0.7)), replace=False)

## create boolean array and set those random values to set those values to True
## for calibration set
cal = np.zeros(len(uniqcsp), dtype=bool)
cal[:] = False

cal[randvals] = True
## for value in randint:
##   cal[value] = True

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
dfmerged.to_csv(csvoutfile)

# subset the records into calibration and validation sets and write out to 
# separate files.
## dfmerged_cal = dfmerged[calrecs]
## dfmerged_val = dfmerged[valrecs]
## dfmerged_cal.to_csv(calcsvoutfile)
## dfmerged_val.to_csv(valcsvoutfile)
