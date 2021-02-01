#!/Volumes/DGE/CAO/caodata/Code/optmemex/bin/python

import warnings
import pickle

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("ignore")
    import spectral.io.envi as envi

from sklearn.ensemble import RandomForestClassifier
import numpy as np
import gdal
from gdalconst import *
import argparse

parser = argparse.ArgumentParser(description='CAO Cloud Masking using RandomForestClassifier.')
parser.add_argument('-i', '--input', help='Input file name', required=True)
parser.add_argument('-o', '--output', help='Output file name', required=True)
parser.add_argument('-m', '--model', help='RandomForest Model name (pickle)', required=True)
args = parser.parse_args()

## show values ##
print ("Input file: %s" % args.input)
print ("Output file: %s" % args.output)
print ("Model file: %s" % args.model)

imgfile = args.input

imgfilehdr = imgfile+'.hdr'
outfilehdr = args.output+'.hdr'

img = envi.open(imgfilehdr)

ncols = img.shape[1]
nrows = img.shape[0]
nbands = img.shape[2]

pkl_fp = open('/Volumes/DGE/CAO/caodata/support/Cloud_Masking/'+args.model, 'rb')
clf = pickle.load(pkl_fp)
pkl_fp.close()

ofid = open(args.output, 'wb')

for i in range(nrows):
  data = img.read_subregion((i,i+1), (0,ncols)) 
  data = data.reshape(ncols, nbands)
  classdata = (clf.predict(data)).astype(np.uint8)
  classdata.tofile(ofid)
  if ((i % 500) == 0):
    print("Finished %d" % i)


ofid.close()
img = None

## Create ENVI header file for output
headerParameters = {}
headerParameters['fileName'] = imgfile
headerParameters['samples'] = '%d' % ncols
headerParameters['lines'] = '%d' % nrows
headerParameters['bandNames'] = 'Sunlit=255;Shade=127;Cloud=63'
## headerParameters['ULlon'] = '147.39'
## headerParameters['ULlat'] = '-25.79'
## headerParameters['pixelSize'] = '9.9e-06'
 
headerText = '''ENVI
description = {{{fileName}}}
samples = {samples}
lines = {lines}
bands = 1
header offset = 0
data type = 1
interleave = bsq
sensor type = Unknown
byte order = 0
band names = {bandNames}
wavelength units = Unknown'''.format(**headerParameters)

## map info = {{Geographic Lat/Lon, 1.000, 1.000, {ULlon}, {ULlat}, {pixelSize}, {pixelSize}, WGS-84, units=Degrees}}
 
headerFile = open(outfilehdr,'w')
headerFile.write(headerText)
headerFile.close()

