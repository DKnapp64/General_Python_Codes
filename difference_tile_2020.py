#!/bin/env python3
import gdal
import numpy as np
import os
import sys
import glob
import subprocess
import datetime

ascdesctile = sys.argv[1]
startat = sys.argv[2]
stopat = sys.argv[3]

tileid = ascdesctile.split('/')[1]
ascdesc = ascdesctile.split('/')[0]

thedirs = glob.glob('20[0-9][0-9][0-1][0-9][0-3][0-9]_to_20[0-9][0-9][0-1][0-9][0-3][0-9]')
files = []

for thedir in thedirs:
  tilepath = thedir + os.path.sep + ascdesctile + '_br_comp.tif'
  if os.path.exists(tilepath):
    files.append(tilepath)

if (len(files) < 2):
  print('Not Enough files for %s...exiting' % (ascdesctile))
  sys.exit(0)

files.sort()
print("Got %d files for tile %s" % (len(files), tileid))
print("First file: %s" % (files[0]))
print("Last file: %s" % (files[-1]))

bleaching_files = []

startdate = datetime.datetime(int(startat[-8:-4]), int(startat[-4:-2]), int(startat[-2:])) + datetime.timedelta(days=1)
stopdate = datetime.datetime(int(stopat[-8:-4]), int(stopat[-4:-2]), int(stopat[-2:])) + datetime.timedelta(days=1)

for j,name in enumerate(files):
  imgdatestr = name.split('_')[0][0:8]
  imgdate = datetime.datetime(int(imgdatestr[0:4]), int(imgdatestr[4:6]), int(imgdatestr[6:]))
  if (imgdate < stopdate) and (imgdate >= startdate):
    bleaching_files.append(name) 

if (len(bleaching_files) < 2):
  print('Not enough times series tiles to do differencing.  Exiting.')
  sys.exit(0)

baselinefile = 'BaseFiles2020/'+tileid+'_base.tif'
if os.path.exists(baselinefile):
  baseDS = gdal.Open(baselinefile, gdal.GA_ReadOnly)
else:
  print('No Basefile %s' % (baselinefile))
  sys.exit(0)

## read maximum band
basedata = baseDS.GetRasterBand(4).ReadAsArray()
baseDS = None

bleaching_datasets = []
for _f in range(len(bleaching_files)):
    bleaching_datasets.append(gdal.Open(bleaching_files[_f],gdal.GA_ReadOnly))
    print((bleaching_files[_f],bleaching_datasets[-1].RasterXSize,bleaching_datasets[-1].RasterYSize))

maskfile = 'Coral/' + tileid + '_gcrmn_reef_extent2.tif'
## maskfile = 'CoralNew/' + tileid + '_coral2.tif'
print('Maskfile %s' % (maskfile))
maskDS = gdal.Open(maskfile, gdal.GA_ReadOnly)
mask = maskDS.GetRasterBand(1).ReadAsArray(0,0,4096,4096)

driver = gdal.GetDriverByName('GTiff')
driver.Register()

x_off = 0
y_off = 0
x_size = bleaching_datasets[0].RasterXSize
y_size = bleaching_datasets[0].RasterYSize

trans = bleaching_datasets[0].GetGeoTransform()
out_trans = list(trans)
out_trans[0] += x_off*trans[1]
out_trans[3] += y_off*trans[5]

n_output_bands = 2
## outname = 'persistant_deviation_{}_{}_{:0>2d}.tif'.format(ascdesc, tileid, stopat)
outdir = '/data/gdcsdata/Research/Researcher/Knapp/SouthChinaSea/AscendingDescending/Persistent_Deviation/'+stopdate.strftime('%Y%m%d')+'/'
if not os.path.exists(outdir):
  os.mkdir(outdir)

outname = 'persistant_deviation_{}_{}_{}.tif'.format(ascdesc, tileid, stopdate.strftime('%Y%m%d'))
outDataset = driver.Create(outdir+outname,x_size,y_size,n_output_bands,gdal.GDT_Float32,options=['COMPRESS=LZW','TILED=YES'])
outDataset.SetProjection(bleaching_datasets[0].GetProjection())
outDataset.SetGeoTransform(out_trans)

change_dat = np.zeros((y_size,x_size,n_output_bands),dtype=np.float32) -9999

for _line in range(y_off, y_off+y_size):

    # get the baseline values
    baseline = np.squeeze(basedata[_line,:])
    maskline = np.squeeze(mask[_line,:])

    # step through bleaching datasets
    n_dev = np.zeros(x_size)
    max_dev = np.zeros(x_size) - 9999

    for _f in range(len(bleaching_datasets)):
        ldat = np.squeeze(bleaching_datasets[_f].ReadAsArray(x_off,_line,x_size,1))

        # add one for each deviation above baseline
        n_dev[ldat > baseline] += 1

        # save the maximum deviation
        max_dev[ldat > baseline] = np.maximum(ldat - baseline, max_dev)[ldat > baseline]
        
    n_dev[maskline == 0] = -9999
    max_dev[maskline == 0] = -9999

    change_dat[_line-y_off,:,0] = n_dev
    change_dat[_line-y_off,:,1] = max_dev

for n in range(change_dat.shape[-1]):
    outDataset.GetRasterBand(n+1).WriteArray(np.squeeze(change_dat[...,n]),0,0)
    outDataset.GetRasterBand(n+1).SetNoDataValue(-9999.)

del outDataset

for thisDS in bleaching_datasets:
  thisDS = None

print(np.histogram(change_dat[change_dat != -9999]))
subprocess.call('gdaladdo {} 2 4 8 16 32 64 128'.format(outdir+outname),shell=True)

