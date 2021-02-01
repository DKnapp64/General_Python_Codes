import gdal
import os, sys
import numpy as np

infiles = ['20190406_moorea_tile_sr.tif', '20190407_moorea_tile_sr.tif', '20190415_moorea_tile_sr.tif', 
'20190507_moorea_tile_sr.tif', '20190517_moorea_tile_sr.tif', '20190603_moorea_tile_sr.tif', 
'20190604_moorea_tile_sr.tif', '20190607_moorea_tile_sr.tif', '20190616_moorea_tile_sr.tif']

sampfile = 'sample_coral_areas.tif'

outfile = "moorea_sample_coral_output.csv"

sDS = gdal.Open(sampfile, gdal.GA_ReadOnly)
samparr = sDS.GetRasterBand(1).ReadAsArray(3206,760,800,390)
sDS = None

sampids = np.unique(samparr)
if (sampids[0] == 0):
  sampids = sampids[1:] 

means = np.zeros((len(infiles), sampids.shape[0], 2), dtype=np.float32) 
sdevs = np.zeros((len(infiles), sampids.shape[0], 2), dtype=np.float32) 

for j,thefile in enumerate(infiles):
  inDS = gdal.Open(thefile, gdal.GA_ReadOnly)
  blue = inDS.GetRasterBand(1).ReadAsArray(3206,760,800,390)
  green = inDS.GetRasterBand(2).ReadAsArray(3206,760,800,390)
  for k,thesamp in enumerate(sampids):
    thissamp = np.logical_and(np.equal(samparr, thesamp), np.not_equal(blue, 0.0))
    means[j,k,0] = np.mean(blue[thissamp])
    sdevs[j,k,0] = np.std(blue[thissamp])
    means[j,k,1] = np.mean(green[thissamp])
    sdevs[j,k,1] = np.std(green[thissamp])

inDS = None

f = open(outfile, 'w')

for i,thissamp in enumerate(sampids):
  bluestring = ''
  greenstring = ''
  for j,thedate in enumerate(infiles):
    bluestring += ("%7.1f,") % (means[j,i,0]/100.0)
    greenstring += ("%7.1f,") % (means[j,i,1]/100.0)
  for j,thedate in enumerate(infiles):
    bluestring += ("%7.1f,") % (sdevs[j,i,0]/100.0)
    greenstring += ("%7.1f,") % (sdevs[j,i,1]/100.0)
  bluestring = bluestring[0:-1] + '\n'
  greenstring = greenstring[0:-1] + '\n'
  f.write(bluestring)
  f.write(greenstring)

f.close()
