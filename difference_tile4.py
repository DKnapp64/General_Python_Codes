#!/bin/env python3
import gdal
import numpy as np
import os
import sys
import yaml
import glob
import subprocess
import datetime
from scipy import interpolate
import pdb

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

baseline_files = [x for x in files if '201908' not in x and '201909' not in x and '201910' not in x]
temp_bleaching_files = [x for x in files if '201908' in x or '201909' in x or '201910' in x]
bleaching_files = []

stopdate = datetime.datetime(int(stopat[-8:-4]), int(stopat[-4:-2]), int(stopat[-2:])) + datetime.timedelta(days=1)

for j,name in enumerate(temp_bleaching_files):
  imgdatestr = name.split('_')[3][0:8]
  imgdate = datetime.datetime(int(imgdatestr[0:4]), int(imgdatestr[4:6]), int(imgdatestr[6:]))
  if (imgdate < stopdate):
    bleaching_files.append(name) 

if (len(bleaching_files) < 2):
  print('Not enough times series tiles to do differencing.  Exiting.')
  sys.exit(0)

datasets = []
for _f in range(len(baseline_files)):
    datasets.append(gdal.Open(baseline_files[_f],gdal.GA_ReadOnly))
    print((baseline_files[_f],datasets[-1].RasterXSize,datasets[-1].RasterYSize))

bleaching_datasets = []
for _f in range(len(bleaching_files)):
    bleaching_datasets.append(gdal.Open(bleaching_files[_f],gdal.GA_ReadOnly))
    print((bleaching_files[_f],bleaching_datasets[-1].RasterXSize,bleaching_datasets[-1].RasterYSize))

maskfile = 'CoralTiles10m/' + tileid + '_coral.tif'
sandmaskfile = 'coralsand/' + tileid + '_sand.tif'
sandfile = 'coralsand/' + ascdesc + '_' + tileid + '_baselinesand.tif'
sandcoarsefile = 'coralsand/' + ascdesc + '_' + tileid + '_baselinesand_coarse.tif'
print('Maskfile %s' % (maskfile))
maskset = gdal.Open(maskfile, gdal.GA_ReadOnly)

driver = gdal.GetDriverByName('GTiff')
driver.Register()

x_off = 0
y_off = 0
x_size = datasets[0].RasterXSize
y_size = datasets[0].RasterYSize

trans = datasets[0].GetGeoTransform()

n_output_bands = 2
## outname = 'persistant_deviation_{}_{}_{:0>2d}.tif'.format(ascdesc, tileid, stopat)
outname = 'persistant_deviation_{}_{}_{}.tif'.format(ascdesc, tileid, stopdate.strftime('%Y%m%d'))
adjustname = 'persistant_deviation_adj_{}_{}_{}.tif'.format(ascdesc, tileid, stopdate.strftime('%Y%m%d'))
outDataset = driver.Create(outname,x_size,y_size,n_output_bands,gdal.GDT_Float32,options=['COMPRESS=DEFLATE','TILED=YES'])
outDataset.SetProjection(datasets[0].GetProjection())
outDataset.SetGeoTransform(trans)

aDS = driver.Create(adjustname,x_size,y_size,len(datasets),gdal.GDT_Int16,options=['COMPRESS=LZW','TILED=YES'])
aDS.SetProjection(datasets[0].GetProjection())
aDS.SetGeoTransform(trans)

change_dat = np.zeros((4096,4096,n_output_bands),dtype=np.float32) - 9999

## read the sandbaseline data and corresponding coarse data
if os.path.exists(sandfile):
  bDS = gdal.Open(sandfile, gdal.GA_ReadOnly)
  bBand1 = bDS.GetRasterBand(1)
  bBand2 = bDS.GetRasterBand(2)
  sandmean = bBand1.ReadAsArray()
  sandsdev = bBand2.ReadAsArray()
  bDS = None
else:
  print("file %s does not exist." % (sandfile))
  outDataset = None
  sys.exit(0)

if os.path.exists(sandmaskfile):
  smDS = gdal.Open(sandmaskfile, gdal.GA_ReadOnly)
  smBand1 = smDS.GetRasterBand(1)
  sandmask = smBand1.ReadAsArray()
  sandbool = np.equal(sandmask, 1)
  smDS = None
else:
  print("file %s does not exist." % (sandmaskfile))
  outDataset = None
  sys.exit(0)

if os.path.exists(sandcoarsefile):
  bsDS = gdal.Open(sandcoarsefile, gdal.GA_ReadOnly)
  bsBand1 = bsDS.GetRasterBand(1)
  bsBand2 = bsDS.GetRasterBand(2)
  sandcmean = bsBand1.ReadAsArray()
  sandcsdev = bsBand2.ReadAsArray()
  bsDS = None
else:
  print("file %s does not exist." % (sandcoarsefile))
  outDataset = None
  sys.exit(0)

print("Baseline  DataSets: %d" % len(datasets))
print("Bleaching DataSets: %d" % len(bleaching_datasets))

for _patch in range(16*16):
  xoff = (_patch % 16)
  yoff = (_patch//16)
  xend = xoff + 256
  yend = yoff + 256

  # get the baseline values
  patch_dat = np.zeros((256,256,len(datasets)))
  for _f in range(len(baseline_files)):
    patch_dat[...,_f] = np.squeeze(datasets[_f].ReadAsArray(xoff,yoff,256,256))
      
  # merge those values together to determine baseline
  patch_dat[patch_dat == -9999] = np.nan
  baseline = np.nanmax(patch_dat, axis=-1)

  # step through bleaching datasets
  n_dev = np.zeros((256, 256))
  max_dev = np.zeros((256,256)) - 9999

  #  if number of points in the baseline 256x256 patch is small, let's say 5, 
  ## write out blank data for that patch and continue to next patchskip it
  if (np.sum(np.isfinite(baseline)) < 5):
    for _f in range(len(bleaching_datasets)):
      aDS.GetRasterBand(_f+1).WriteArray(np.zeros((256, 256))-9999.0, xoff, yoff)
      continue
    
  for _f in range(len(bleaching_datasets)):
    smean = np.squeeze(sandmean[yoff:yend, xoff:xend])
    ldat = np.squeeze(bleaching_datasets[_f].ReadAsArray(xoff,yoff,256,256))
    smask = np.squeeze(sandbool[yoff:yend, xoff:xend])
    miss = np.logical_or(np.equal(smean, -9999), np.equal(ldat, -9999))
    missldat = np.equal(ldat, -9999)
    missmean = np.equal(smean, -9999)
    scoarse = np.repeat(np.repeat(sandcmean[yoff//16:(yoff//16 + 16), xoff//16:(xoff//16 + 16)], 16, axis=0), 16, axis=1)
    if np.all(np.equal(scoarse[missmean], -9999)): 
      adj = np.zeros((256, 256))
      aDS.GetRasterBand(_f+1).WriteArray(adj.astype(np.int16), xoff, yoff)
      continue
    else:
      smean[missmean] = scoarse[missmean]
    smasknotmiss = np.logical_and(np.logical_not(miss), smask)
    if (np.sum(smasknotmiss) == 0):
      smean = scoarse.copy() 
    sanddiffs = ldat[smasknotmiss] - smean[smasknotmiss]
    ## if (np.sum(smasknotmiss) > 5):
    ##   fill = np.interp(np.nonzero(np.logical_not(smasknotmiss)), np.nonzero(smasknotmiss), sanddiffs)
    ## else: 
    ##   continue
    goodpnt = np.nonzero(np.logical_not(smasknotmiss))
    fillpnt = np.nonzero(smasknotmiss)
    if (np.sum(smasknotmiss) > 0):
      interpfunc = interpolate.SmoothBivariateSpline(goodpnt[0], goodpnt[1], sanddiffs)
      fill = interpfunc.ev(fillpnt[0], fillpnt[1])
      adj = np.zeros((256,256))
      adj[goodpnt] = sanddiffs
      adj[fillpnt] = fill
    else:
      adj = np.zeros((256,256))
    ## adj[np.logical_not(smasknotmiss)] = fill
    ## smalldiff = np.logical_and(np.less(ldat, ldat + (sandsdev*2)), np.greater(ldat, ldat - (sandsdev*2)))
    ## goodgood = np.logical_and(smask, smalldiff)
    ldatadj = ldat-adj
    # add one for each deviation above baseline
    n_dev[ldatadj > baseline] += 1
    ## ldatadj[np.logical_not(smalldiff)] = 0
    
    # save the maximum deviation
    max_dev[ldatadj > baseline] = np.maximum(ldatadj-baseline, max_dev)[ldatadj > baseline]

    aDS.GetRasterBand(_f+1).WriteArray(adj.astype(np.int16), xoff, yoff)
    

    mask = maskset.ReadAsArray(xoff,yoff,256,256)

    n_dev[mask == 0] = -9999
    max_dev[mask == 0] = -9999

    change_dat[yoff:yend, xoff:xend,0] = n_dev
    change_dat[yoff:yend, xoff:xend,1] = max_dev


for n in range(change_dat.shape[-1]):
    outDataset.GetRasterBand(n+1).WriteArray(change_dat[...,n],0,0)
    outDataset.GetRasterBand(n+1).SetNoDataValue(-9999)

del outDataset
del aDS

for thisDS in bleaching_datasets:
  thisDS = None

for thisDS in datasets:
  thisDS = None

print(np.histogram(change_dat[change_dat != -9999]))
subprocess.call('gdaladdo {} 2 4 8 16 32 64 128'.format(outname),shell=True)

