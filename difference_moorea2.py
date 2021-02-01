#!/bin/env python3
import argparse
import gdal
import numpy as np
import pandas as pd
import os
import sys
import yaml
from tqdm import tqdm
import glob
import subprocess
import datetime

tileid = sys.argv[1]
ascdesc = sys.argv[2]
stopat = sys.argv[3]

thedirs = glob.glob(ascdesc + '_20[0-9][0-9][0-1][0-9][0-3][0-9]_to_20[0-9][0-9][0-1][0-9][0-3][0-9]')
files = []

for thedir in thedirs:
  tilepath = thedir + os.path.sep + tileid + '_br_comp.tif'
  if os.path.exists(tilepath):
    files.append(tilepath)

files.sort()
print("Got %d files for tile %s" % (len(files), tileid))
print("First file: %s" % (files[0]))
print("Last file: %s" % (files[-1]))

## baseline_files = [x for x in files if '201812' in x or '201901' in x or '201902' in x]
temp_bleaching_files = [x for x in files if '201812' not in x and '201901' not in x and '201902' not in x]
bleaching_files = []

stopdate = datetime.datetime(int(stopat[-8:-4]), int(stopat[-4:-2]), int(stopat[-2:])) + datetime.timedelta(days=1)

for j,name in enumerate(temp_bleaching_files):
  imgdatestr = name.split('_')[3][0:8]
  imgdate = datetime.datetime(int(imgdatestr[0:4]), int(imgdatestr[4:6]), int(imgdatestr[6:]))
  if (imgdate < stopdate):
    bleaching_files.append(name) 

## datasets = []

print('####################################################')
print('##              BASELINE FILES                    ##')
print('####################################################')

## Read Baseline Data set for the tile
baselinefile = '/data/gdcsdata/Research/Researcher/Knapp/Moorea_Weekly/AscendingDescending/BaseFiles/'+ascdesc+'_'+tileid+'_base.tif'
baseDS = gdal.Open(baselinefile, gdal.GA_ReadOnly)
## Read the Max band (Band order is (Mean, SDev, Min, Max, Median)
baseband = baseDS.GetRasterBand(4).ReadAsArray()

## for _f in range(len(baseline_files)):
##     datasets.append(gdal.Open(baseline_files[_f],gdal.GA_ReadOnly))
##     print((baseline_files[_f],datasets[-1].RasterXSize,datasets[-1].RasterYSize))

print('####################################################')
print('##              BLEACHING FILES                   ##')
print('####################################################')

bleaching_datasets = []
for _f in range(len(bleaching_files)):
    bleaching_datasets.append(gdal.Open(bleaching_files[_f],gdal.GA_ReadOnly))
    print((bleaching_files[_f],bleaching_datasets[-1].RasterXSize,bleaching_datasets[-1].RasterYSize))

if (len(bleaching_files) < 2):
  print('Not enough times series tiles to do differencing.  Exiting.')
  sys.exit(0)

maskfile = 'CoralNew/' + tileid + '_coral3.tif'
## maskfile = 'CoralTiles10m/' + tileid + '_coral.tif'
if os.path.exists(maskfile):
  print('Maskfile %s' % (maskfile))
  maskset = gdal.Open(maskfile, gdal.GA_ReadOnly)

driver = gdal.GetDriverByName('GTiff')
driver.Register()

x_off = 0
y_off = 0
## x_size = datasets[0].RasterXSize
## y_size = datasets[0].RasterYSize
x_size = baseDS.RasterXSize
y_size = baseDS.RasterYSize

trans = baseDS.GetGeoTransform()
out_trans = list(trans)
out_trans[0] += x_off*trans[1]
out_trans[3] += y_off*trans[5]

n_output_bands = 2
## outname = 'persistant_deviation_{}_{}_{:0>2d}.tif'.format(ascdesc, tileid, stopat)
outdir = '/data/gdcsdata/Research/Researcher/Knapp/Moorea_Weekly/AscendingDescending/Persistent_Deviation/'+stopdate.strftime('%Y%m%d')+'/'
outname = 'persistant_deviation_{}_{}_{}.tif'.format(ascdesc, tileid, stopdate.strftime('%Y%m%d'))
outDataset = driver.Create(outdir+outname,x_size,y_size,n_output_bands,gdal.GDT_Int16,options=['COMPRESS=LZW','TILED=YES'])
outDataset.SetProjection(baseDS.GetProjection())
outDataset.SetGeoTransform(out_trans)
baseDS = None

change_dat = np.zeros((y_size,x_size,n_output_bands),dtype=np.float32) - 9999

for _line in range(y_off, y_off+y_size):

    # get the baseline values
    ## line_dat = np.zeros((x_size,len(datasets)))
    ## for _f in range(len(baseline_files)):
    ##     line_dat[:,_f] = np.squeeze(datasets[_f].ReadAsArray(x_off,_line,x_size,1))

    # merge those values together to determine baseline
    ## line_dat[line_dat == -9999] = np.nan
    ## baseline = np.nanmax(line_dat,axis=1)
    baseline = baseband[_line,:]

    # step through bleaching datasets
    n_dev = np.zeros(x_size)
    max_dev = np.zeros(x_size) - 9999
    for _f in range(len(bleaching_datasets)):
        ldat = np.squeeze(bleaching_datasets[_f].ReadAsArray(x_off,_line,x_size,1))

        # add one for each deviation above baseline
        n_dev[ldat > baseline] += 1

        # save the maximum deviation
        max_dev[ldat > baseline] = np.maximum(ldat - baseline, max_dev)[ldat > baseline]
        
    #rel_mask[mask == 0] = False

    #change_dat[_line-y_off,rel_mask,0] = line_dat[rel_mask,-1] - maxs[rel_mask]
    #
    #rel_mask = np.logical_and(rel_mask, line_dat[:,-2] > maxs)
    #change_dat[_line-y_off,rel_mask,1] = line_dat[rel_mask,-1] - maxs[rel_mask]

    if (os.path.exists(maskfile)):
      mask = np.squeeze(maskset.ReadAsArray(x_off,_line,x_size,1))
    else:
      mask = np.ones((x_size)).astype(np.uint8)

    n_dev[mask == 0] = -9999
    max_dev[mask == 0] = -9999

    change_dat[_line-y_off,:,0] = n_dev
    change_dat[_line-y_off,:,1] = max_dev

if (os.path.exists(maskfile)):
  maskset = None

for n in range(change_dat.shape[-1]):
    outDataset.GetRasterBand(n+1).WriteArray(np.squeeze(change_dat[...,n]),0,0)
    outDataset.GetRasterBand(n+1).SetNoDataValue(-9999)
del outDataset

for thisDS in bleaching_datasets:
  thisDS = None

## for thisDS in datasets:
##   thisDS = None

print(np.histogram(change_dat[change_dat != -9999]))
subprocess.call('gdaladdo {} 2 4 8 16 32 64 128'.format(outdir+outname),shell=True)

