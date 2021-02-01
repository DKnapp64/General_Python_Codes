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

## base_dir = 'kanbay'
tileid = sys.argv[1]
ascdesc = sys.argv[2]
## stopat = int(sys.argv[3])

thedirs = glob.glob(ascdesc + '_20[0-9][0-9][0-1][0-9][0-3][0-9]_to_20[0-9][0-9][0-1][0-9][0-3][0-9]')
files = []

## if (base_dir not in ['kanbay','kauai']):
##     print('invalid base_dir')
##     quit()

for thedir in thedirs:
  tilepath = thedir + os.path.sep + tileid + '_br_comp.tif'
  if os.path.exists(tilepath):
    files.append(tilepath)

## files = glob.glob(os.path.join(base_dir,'descending_*.tif'))
## files = glob.glob(os.path.join(base_dir,'ascending_*.tif'))

files.sort()
print("Got %d files for tile %s" % (len(files), tileid))
print("First file: %s" % (files[0]))
print("Last file: %s" % (files[-1]))

baseline_files = [x for x in files if '201908' not in x and '201909' not in x and '201910' not in x]
bleaching_files = [x for x in files if '201908' in x or '201909' in x or '201910' in x]
## bleaching_files = bleaching_files[0:stopat]

datasets = []
for _f in range(len(baseline_files)):
    datasets.append(gdal.Open(baseline_files[_f],gdal.GA_ReadOnly))
    print((baseline_files[_f],datasets[-1].RasterXSize,datasets[-1].RasterYSize))

bleaching_datasets = []
for _f in range(len(bleaching_files)):
    bleaching_datasets.append(gdal.Open(bleaching_files[_f],gdal.GA_ReadOnly))
    print((bleaching_files[_f],bleaching_datasets[-1].RasterXSize,bleaching_datasets[-1].RasterYSize))

maskfile = 'CoralTiles10m/' + tileid + '_coral.tif'
print('Maskfile %s' % (maskfile))
maskset = gdal.Open(maskfile, gdal.GA_ReadOnly)

driver = gdal.GetDriverByName('GTiff')
driver.Register()

#[upper_lefts, mask_ul], x_size, y_size = common_io.get_overlapping_extent([datasets, [maskset]])

#ul = [-17576462,2459318]
#lr = [-17548391,2420253]
#
#x_off =  int((ul[0] - trans[0]) / trans[1])
#y_off =  int((ul[1] - trans[3]) / trans[5])
#x_size = int((lr[0] - ul[0]) / trans[1])
#y_size = int((lr[1] - ul[1]) / trans[5])
#print((x_off,y_off,x_size,y_size))

x_off = 0
y_off = 0
x_size = datasets[0].RasterXSize
y_size = datasets[0].RasterYSize

trans = datasets[0].GetGeoTransform()
out_trans = list(trans)
out_trans[0] += x_off*trans[1]
out_trans[3] += y_off*trans[5]

n_output_bands = 2
## outname = 'persistant_deviation_{}_{}_{:0>2d}.tif'.format(ascdesc, tileid, stopat)
outname = 'persistant_deviation_{}_{}.tif'.format(ascdesc, tileid)
outDataset = driver.Create(outname,x_size,y_size,n_output_bands,gdal.GDT_Float32,options=['COMPRESS=DEFLATE','TILED=YES'])
outDataset.SetProjection(datasets[0].GetProjection())
outDataset.SetGeoTransform(out_trans)

change_dat = np.zeros((y_size,x_size,n_output_bands),dtype=np.float32) -9999
for _line in tqdm(range(y_off, y_off+y_size),ncols=80):

    # get the baseline values
    line_dat = np.zeros((x_size,len(datasets)))
    for _f in range(len(baseline_files)):
        line_dat[:,_f] = np.squeeze(datasets[_f].ReadAsArray(x_off,_line,x_size,1))

    # merge those values together to determine baseline
    line_dat[line_dat == -9999] = np.nan
    baseline = np.nanmax(line_dat,axis=1)

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

    mask = np.squeeze(maskset.ReadAsArray(x_off,_line,x_size,1))

    n_dev[mask == 0] = -9999
    max_dev[mask == 0] = -9999

    change_dat[_line-y_off,:,0] = n_dev
    change_dat[_line-y_off,:,1] = max_dev

for n in range(change_dat.shape[-1]):
    outDataset.GetRasterBand(n+1).WriteArray(np.squeeze(change_dat[...,n]),0,0)
    outDataset.GetRasterBand(n+1).SetNoDataValue(-9999)
del outDataset

for thisDS in bleaching_datasets:
  thisDS = None

for thisDS in datasets:
  thisDS = None

print(np.histogram(change_dat[change_dat != -9999]))
subprocess.call('gdaladdo {} 2 4 8 16 32 64 128'.format(outname),shell=True)


