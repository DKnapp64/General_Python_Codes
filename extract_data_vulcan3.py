import gdal
import os, sys
import numpy as np

## infiles = ['20190406_moorea_tile_sr_rb.tif', '20190407_moorea_tile_sr_rb.tif', '20190415_moorea_tile_sr_rb.tif', 
## '20190507_moorea_tile_sr_rb.tif', '20190517_moorea_tile_sr_rb.tif', '20190603_moorea_tile_sr_rb.tif', 
## '20190604_moorea_tile_sr_rb.tif', '20190607_moorea_tile_sr_rb.tif', '20190616_moorea_tile_sr_rb.tif']

os.chdir("/scratch/dknapp4/Moorea_for_Nick")

infiles =  ['20181230_moorea_tile_sr_rb.tif', '20190115_moorea_tile_sr_rb.tif',
  '20190117_moorea_tile_sr_rb.tif', '20190118_moorea_tile_sr_rb.tif',
  '20190123_moorea_tile_sr_rb.tif', '20190208_moorea_tile_sr_rb.tif',
  '20190227_moorea_tile_sr_rb.tif', '20190301_moorea_tile_sr_rb.tif',
  '20190307_moorea_tile_sr_rb.tif', '20190318_moorea_tile_sr_rb.tif',
  '20190322_moorea_tile_sr_rb.tif', '20190405_moorea_tile_sr_rb.tif',
  '20190406_moorea_tile_sr_rb.tif', '20190407_moorea_tile_sr_rb.tif',
  '20190415_moorea_tile_sr_rb.tif', '20190507_moorea_tile_sr_rb.tif', 
  '20190517_moorea_tile_sr_rb.tif',
  '20190604_moorea_tile_sr_rb.tif', '20190607_moorea_tile_sr_rb.tif', 
  '20190616_moorea_tile_sr_rb.tif', '20190617_moorea_tile_sr_rb.tif',
  '20190623_moorea_tile_sr_rb.tif', '20190624_moorea_tile_sr_rb.tif', 
  '20190625_moorea_tile_sr_rb.tif', '20190626_moorea_tile_sr_rb.tif', 
  '20190627_moorea_tile_sr_rb.tif', '20190705_moorea_tile_sr_rb.tif', 
  '20190710_moorea_tile_sr_rb.tif', '20190711_moorea_tile_sr_rb.tif', 
  '20190712_moorea_tile_sr_rb.tif', '20190713_moorea_tile_sr_rb.tif']

## infiles = ['20170421_moorea_tile_sr_rb.tif', '20170423_moorea_tile_sr_rb.tif',
##   '20170505_moorea_tile_sr_rb.tif', '20170628_moorea_tile_sr_rb.tif',
##   '20170720_moorea_tile_sr_rb.tif', '20170721_moorea_tile_sr_rb.tif',
##   '20180112_moorea_tile_sr_rb.tif', '20180120_moorea_tile_sr_rb.tif',
##   '20180125_moorea_tile_sr_rb.tif', '20180221_moorea_tile_sr_rb.tif',
##   '20180223_moorea_tile_sr_rb.tif', '20180227_moorea_tile_sr_rb.tif',
##   '20180228_moorea_tile_sr_rb.tif', '20180301_moorea_tile_sr_rb.tif',
##   '20180302_moorea_tile_sr_rb.tif', '20180305_moorea_tile_sr_rb.tif',
##   '20180712_moorea_tile_sr_rb.tif', '20180720_moorea_tile_sr_rb.tif',
##   '20180723_moorea_tile_sr_rb.tif', '20180724_moorea_tile_sr_rb.tif',
##   '20180727_moorea_tile_sr_rb.tif', '20180728_moorea_tile_sr_rb.tif',
##   '20180807_moorea_tile_sr_rb.tif', '20180814_moorea_tile_sr_rb.tif',
##   '20180818_moorea_tile_sr_rb.tif', '20180819_moorea_tile_sr_rb.tif',
##   '20180823_moorea_tile_sr_rb.tif', '20180830_moorea_tile_sr_rb.tif',
##   '20180905_moorea_tile_sr_rb.tif', '20180915_moorea_tile_sr_rb.tif',
##   '20180920_moorea_tile_sr_rb.tif', '20181005_moorea_tile_sr_rb.tif',
##   '20181008_moorea_tile_sr_rb.tif', '20181017_moorea_tile_sr_rb.tif',
##   '20181101_moorea_tile_sr_rb.tif', '20181110_moorea_tile_sr_rb.tif',
##   '20181111_moorea_tile_sr_rb.tif', '20181122_moorea_tile_sr_rb.tif',
##   '20181129_moorea_tile_sr_rb.tif', '20181130_moorea_tile_sr_rb.tif',
##   '20181204_moorea_tile_sr_rb.tif', '20181214_moorea_tile_sr_rb.tif',
##   '20181223_moorea_tile_sr_rb.tif', '20181229_moorea_tile_sr_rb.tif',
##   '20181230_moorea_tile_sr_rb.tif', '20190115_moorea_tile_sr_rb.tif',
##   '20190117_moorea_tile_sr_rb.tif', '20190118_moorea_tile_sr_rb.tif',
##   '20190123_moorea_tile_sr_rb.tif', '20190208_moorea_tile_sr_rb.tif',
##   '20190227_moorea_tile_sr_rb.tif', '20190301_moorea_tile_sr_rb.tif',
##   '20190307_moorea_tile_sr_rb.tif', '20190318_moorea_tile_sr_rb.tif',
##   '20190322_moorea_tile_sr_rb.tif', '20190405_moorea_tile_sr_rb.tif',
##   '20190406_moorea_tile_sr_rb.tif', '20190407_moorea_tile_sr_rb.tif',
##   '20190414_moorea_tile_sr_rb.tif', '20190415_moorea_tile_sr_rb.tif',
##   '20190505_moorea_tile_sr_rb.tif', '20190508_moorea_tile_sr_rb.tif',
##   '20190515_moorea_tile_sr_rb.tif', '20190517_moorea_tile_sr_rb.tif',
##   '20190604_moorea_tile_sr_rb.tif',
##   '20190607_moorea_tile_sr_rb.tif', '20190616_moorea_tile_sr_rb.tif']

print("Number of files: %d" % (len(infiles)))

sampfile = '/scratch/dknapp4/Western_Hawaii/Moorea/sample_coral_areas.tif'

outfile = "/scratch/dknapp4/Western_Hawaii/Moorea/moorea_sample_coral_output_rb_20190715.csv"

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
  print("%s" % (thefile))
  if (inDS is None):
    print("File %s not found" % (thefile))
    sDS = None
    sys.exit(1)
  blue = inDS.GetRasterBand(1).ReadAsArray(3206,760,800,390)
  green = inDS.GetRasterBand(2).ReadAsArray(3206,760,800,390)
  for k,thesamp in enumerate(sampids):
    ## thissamp = np.logical_and(np.equal(samparr, thesamp), np.not_equal(blue, 0.0))
    thissamp = np.logical_and(np.equal(samparr, thesamp), np.not_equal(blue, -9999.0))
    if (thissamp.sum() > 0):
      means[j,k,0] = np.mean(blue[thissamp])
      sdevs[j,k,0] = np.std(blue[thissamp])
      means[j,k,1] = np.mean(green[thissamp])
      sdevs[j,k,1] = np.std(green[thissamp])
    else:
      means[j,k,0] = -900
      sdevs[j,k,0] = -900
      means[j,k,1] = -900
      sdevs[j,k,1] = -900
  inDS = None

f = open(outfile, 'w')
headit = 'Date, Blue1, Blue2, Blue3, Blue4, Blue5, Blue6, Blue7, Blue8,' 
headit += 'Green1, Green2, Green3, Green4, Green5, Green6, Green7, Green8,' 
headit += 'BlueSD1, BlueSD2, BlueSD3, BlueSD4, BlueSD5, BlueSD6, BlueSD7, BlueSD8,' 
headit += 'GreenSD1, GreenSD2, GreenSD3, GreenSD4, GreenSD5, GreenSD6, GreenSD7, GreenSD8\n' 

f.write(headit)

for j,thefile in enumerate(infiles):
  bluestringmeans = ''
  greenstringmeans = ''
  bluestringsd = ''
  greenstringsd = ''
  for i,thesamp in enumerate(sampids):
    bluestringmeans += ("%.1f,") % (means[j,i,0]/100.0)
    greenstringmeans += ("%.1f,") % (means[j,i,1]/100.0)
    bluestringsd += ("%.1f,") % (sdevs[j,i,0]/100.0)
    greenstringsd += ("%.1f,") % (sdevs[j,i,1]/100.0)
  bigstring = thefile[0:8] + ', ' + bluestringmeans + greenstringmeans + bluestringsd + greenstringsd[0:-1] + '\n'
  f.write(bigstring)

f.close()
