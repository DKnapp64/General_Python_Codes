#!/bin/env python3
import gdal
import os, sys
import numpy as np
import math

rootnames = ['L15-0123E-1148N', 'L15-0123E-1149N', 'L15-0124E-1147N', 
             'L15-0124E-1148N', 'L15-0124E-1149N', 'L15-0124E-1150N', 
             'L15-0125E-1147N', 'L15-0125E-1148N', 'L15-0125E-1149N', 
             'L15-0125E-1150N', 'L15-0126E-1147N', 'L15-0126E-1148N', 
             'L15-0126E-1149N', 'L15-0127E-1147N', 'L15-0127E-1148N', 
             'L15-0136E-1134N', 'L15-0136E-1135N', 'L15-0136E-1136N', 
             'L15-0136E-1137N', 'L15-0136E-1138N', 'L15-0136E-1139N', 
             'L15-0136E-1140N', 'L15-0136E-1141N', 'L15-0137E-1133N', 
             'L15-0137E-1134N', 'L15-0137E-1135N', 'L15-0137E-1139N', 
             'L15-0137E-1140N', 'L15-0137E-1141N', 'L15-0138E-1133N']

sandend = '_pseudomerc.tif'
coralend = '_pseudomerc_livecoral.tif'

coordfile = "webpoints_out2.csv"
ptf = open(coordfile, 'r')
coordlines = ptf.readlines()
coordarr = np.zeros((len(coordlines), 2))

for d,temp in enumerate(coordlines):
  coordarr[d,0] = float(temp.split()[0])
  coordarr[d,1] = float(temp.split()[1])
  
## rbdir = '/scratch/dknapp4/Hawaii_Weekly/AscendingDescending/'
rbdir = '/scratch/pbrodrick/bleaching_web_graphics/bottom_reprocess/'
weeks = ['20190701_to_20190708', '20190708_to_20190715', '20190715_to_20190722',
         '20190722_to_20190729', '20190729_to_20190805', '20190805_to_20190812',
         '20190812_to_20190819', '20190819_to_20190826', '20190826_to_20190902',
         '20190902_to_20190909', '20190909_to_20190916', '20190916_to_20190923']
ascdesc = 'descending_'

outfile = "hawaii_sand_coral_stats.csv"
fout = open(outfile, 'w')

for j,myroot in enumerate(rootnames):
  sandfile = myroot + sandend 
  coralfile = myroot + coralend
  sDS = gdal.Open(sandfile, gdal.GA_ReadOnly)
  sand = sDS.GetRasterBand(1).ReadAsArray()
  cDS = gdal.Open(coralfile, gdal.GA_ReadOnly)
  coral = cDS.GetRasterBand(1).ReadAsArray()
  sDS, cDS = None, None
  sandpix = np.logical_and(np.equal(sand, 1), np.not_equal(coral, 1))
  coralpix = np.logical_and(np.not_equal(sand, 1), np.equal(coral, 1))
  for k,mydate in enumerate(weeks):
    rbfile = rbdir + ascdesc + mydate + os.sep + myroot + '_br.tif'
    if not os.path.exists(rbfile):
      print("%s does not exist." % (rbfile))
      continue
    rbDS = gdal.Open(rbfile, gdal.GA_ReadOnly)
    print("%s" % (rbfile))
    gt = rbDS.GetGeoTransform() 
    for d in range(coordarr.shape[0]):
      xoff = math.floor((coordarr[d,0] - gt[0])/gt[1])
      yoff = math.floor((coordarr[d,1] - gt[3])/gt[5])
      if ((xoff >= (rbDS.RasterXSize-100)) or (xoff < 100) or
        (yoff >= (rbDS.RasterYSize-100)) or (yoff < 100)):
        # not in the image, so skip
        continue
      extents = [(xoff-100), (yoff-100), (xoff+100), (yoff+100)] 
      chunk = rbDS.GetRasterBand(1).ReadAsArray(extents[0], extents[1], 200, 200)
      print("%f %f" % (np.min(chunk), np.max(chunk)))
      sandmask = sandpix[extents[1]:extents[3], extents[0]:extents[2]]
      coralmask = coralpix[extents[1]:extents[3], extents[0]:extents[2]]
      goodsand = np.logical_and(sandmask, np.greater(chunk, 0))
      numsand = np.sum(goodsand)
      goodcoral = np.logical_and(coralmask, np.greater(chunk, 0))
      numcoral = np.sum(goodcoral)
      if (numsand > 0):
        sandmean = np.mean(chunk[goodsand])
        sandsd = np.std(chunk[goodsand])
      else:
        sandmean = -9999.
        sandsd = -9999.
      if (numcoral > 0):
        coralmean = np.mean(chunk[goodcoral])
        coralsd = np.std(chunk[goodcoral])
      else:
        coralmean = -9999.
        coralsd = -9999.
      fout.write(("%s, %s, %16.2f, %16.2f, %12.4f, %12.4f, %12.4f, %12.4f\n") 
        % (myroot, mydate, coordarr[d,0], coordarr[d,1], sandmean, sandsd, coralmean, coralsd))  
    ## when you've gone through all the points, clode hte Rb file and go on to next.
    rbDS = None

  ## when you've gone through all the dates for the tile, close the coral and sand files
  ## for that tile and go on to next.
  cDS, sDS = None, None

