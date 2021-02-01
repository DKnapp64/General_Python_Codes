import gdal
from gdalconst import *
import ogr
import numpy as np
import spectral.io.envi as envi
import pdb

indir = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Belize_stuff/ortho/'
outfile = 'test_best_mosaic'
testing = infiles[0]
timg = envi.read_envi_header(indir+testing+'.hdr')
metadata = timg.copy()
## metadata['bands'] = '%i' % sum(const.use_out)
## metadata['interleave'] = 'bil'
## metadata['wavelength'] = ['%7.2f'%w for w in wl[const.use_out]]
## metadata['fwhm'] = ['%7.2f'%w for w in fwhm[const.use_out]]
## metadata['data type'] = '4'

infiles = ['CASI_2017_04_11_140827_rgb_ort', 'CASI_2017_04_11_141408_rgb_ort', 
           'CASI_2017_04_11_142021_rgb_ort', 'CASI_2017_04_11_142709_rgb_ort', 
           'CASI_2017_04_11_143903_rgb_ort', 'CASI_2017_04_11_144519_rgb_ort', 
           'CASI_2017_04_11_144847_rgb_ort', 'CASI_2017_04_11_145350_rgb_ort', 
           'CASI_2017_04_11_145830_rgb_ort', 'CASI_2017_04_11_150358_rgb_ort', 
           'CASI_2017_04_11_150953_rgb_ort', 'CASI_2017_04_11_151613_rgb_ort', 
           'CASI_2017_04_11_152207_rgb_ort', 'CASI_2017_04_11_152805_rgb_ort', 
           'CASI_2017_04_11_153422_rgb_ort', 'CASI_2017_04_11_154033_rgb_ort', 
           'CASI_2017_04_11_154653_rgb_ort', 'CASI_2017_04_11_155337_rgb_ort', 
           'CASI_2017_04_11_155934_rgb_ort', 'CASI_2017_04_11_160605_rgb_ort', 
           'CASI_2017_04_11_161251_rgb_ort', 'CASI_2017_04_11_162024_rgb_ort', 
           'CASI_2017_04_11_162644_rgb_ort', 'CASI_2017_04_11_163318_rgb_ort', 
           'CASI_2017_04_11_163937_rgb_ort', 'CASI_2017_04_11_164602_rgb_ort', 
           'CASI_2017_04_11_165518_rgb_ort', 'CASI_2017_04_11_165811_rgb_ort', 
           'CASI_2017_04_11_201113_rgb_ort', 'CASI_2017_04_11_201628_rgb_ort', 
           'CASI_2017_04_11_202011_rgb_ort', 'CASI_2017_04_11_202442_rgb_ort', 
           'CASI_2017_04_12_185329_rgb_ort', 'CASI_2017_04_12_185754_rgb_ort', 
           'CASI_2017_04_12_190551_rgb_ort', 'CASI_2017_04_12_191253_rgb_ort', 
           'CASI_2017_04_12_191916_rgb_ort', 'CASI_2017_04_12_192533_rgb_ort', 
           'CASI_2017_04_12_193129_rgb_ort', 'CASI_2017_04_12_193717_rgb_ort', 
           'CASI_2017_04_12_194309_rgb_ort', 'CASI_2017_04_12_195344_rgb_ort', 
           'CASI_2017_04_12_195735_rgb_ort', 'CASI_2017_04_12_200059_rgb_ort', 
           'CASI_2017_04_12_200403_rgb_ort', 'CASI_2017_04_12_200837_rgb_ort', 
           'CASI_2017_04_12_201200_rgb_ort', 'CASI_2017_04_12_201604_rgb_ort', 
           'CASI_2017_04_12_201959_rgb_ort', 'CASI_2017_04_12_202352_rgb_ort', 
           'CASI_2017_04_12_202737_rgb_ort', 'CASI_2017_04_12_203333_rgb_ort', 
           'CASI_2017_04_12_203908_rgb_ort', 'CASI_2017_04_12_204504_rgb_ort', 
           'CASI_2017_04_12_204956_rgb_ort', 'CASI_2017_04_12_205555_rgb_ort', 
           'CASI_2017_04_13_201105_rgb_ort', 'CASI_2017_04_13_201745_rgb_ort', 
           'CASI_2017_04_13_202329_rgb_ort', 'CASI_2017_04_13_202925_rgb_ort', 
           'CASI_2017_04_13_203450_rgb_ort', 'CASI_2017_04_13_204038_rgb_ort', 
           'CASI_2017_04_13_204544_rgb_ort', 'CASI_2017_04_13_205115_rgb_ort', 
           'CASI_2017_04_13_205656_rgb_ort', 'CASI_2017_04_13_210311_rgb_ort', 
           'CASI_2017_04_13_211504_rgb_ort', 'CASI_2017_04_13_212118_rgb_ort', 
           'CASI_2017_04_13_212957_rgb_ort', 'CASI_2017_04_13_213507_rgb_ort', 
           'CASI_2017_04_13_214029_rgb_ort', 'CASI_2017_04_13_214518_rgb_ort', 
           'CASI_2017_04_13_215026_rgb_ort', 'CASI_2017_04_13_215539_rgb_ort', 
           'CASI_2017_04_13_215951_rgb_ort', 'CASI_2017_04_13_220413_rgb_ort', 
           'CASI_2017_04_14_140554_rgb_ort', 'CASI_2017_04_14_141428_rgb_ort', 
           'CASI_2017_04_14_141804_rgb_ort', 'CASI_2017_04_14_142127_rgb_ort', 
           'CASI_2017_04_14_142526_rgb_ort', 'CASI_2017_04_14_142853_rgb_ort', 
           'CASI_2017_04_14_143313_rgb_ort', 'CASI_2017_04_14_143648_rgb_ort', 
           'CASI_2017_04_14_144108_rgb_ort', 'CASI_2017_04_14_144447_rgb_ort', 
           'CASI_2017_04_14_144837_rgb_ort', 'CASI_2017_04_14_145252_rgb_ort', 
           'CASI_2017_04_14_145720_rgb_ort', 'CASI_2017_04_14_150155_rgb_ort', 
           'CASI_2017_04_14_150643_rgb_ort', 'CASI_2017_04_14_151117_rgb_ort', 
           'CASI_2017_04_14_151601_rgb_ort', 'CASI_2017_04_14_152047_rgb_ort', 
           'CASI_2017_04_14_152531_rgb_ort', 'CASI_2017_04_14_153020_rgb_ort', 
           'CASI_2017_04_14_153455_rgb_ort', 'CASI_2017_04_14_153955_rgb_ort', 
           'CASI_2017_04_14_154449_rgb_ort', 'CASI_2017_04_14_154958_rgb_ort', 
           'CASI_2017_04_14_155507_rgb_ort', 'CASI_2017_04_14_160033_rgb_ort', 
           'CASI_2017_04_14_160614_rgb_ort', 'CASI_2017_04_14_161143_rgb_ort', 
           'CASI_2017_04_14_161713_rgb_ort', 'CASI_2017_04_14_162240_rgb_ort', 
           'CASI_2017_04_14_163048_rgb_ort', 'CASI_2017_04_14_163548_rgb_ort', 
           'CASI_2017_04_14_164024_rgb_ort', 'CASI_2017_04_14_164514_rgb_ort', 
           'CASI_2017_04_14_165005_rgb_ort', 'CASI_2017_04_14_165332_rgb_ort', 
           'CASI_2017_04_14_165647_rgb_ort', 'CASI_2017_04_14_170002_rgb_ort']

## example for Belize, Lighthouse Reef
ulx = 439372.0
uly = 1932335.0
lrx = 454339.0
lry = 1923440.0

bounds = [ulx, uly, lrx, lry]
filebounds = []

for infile in infiles:
  dataset = gdal.Open(indir+infile, GA_ReadOnly)
  if dataset is None:
    continue
  filedims = [dataset.RasterXSize, dataset.RasterYSize]  
  geotrans = dataset.GetGeoTransform()
  fulx = geotrans[0]
  fuly = geotrans[3]
  flrx = geotrans[0] + (filedims[0] * geotrans[1])
  flry = geotrans[3] + (filedims[1] * geotrans[5])
  filebounds.append([fulx, fuly, flrx, flry])
  nbands = dataset.RasterCount
  dataset = None  # close the dataset

pixres = geotrans[1]
ncols = int((lrx - ulx)/pixres)
nrows = int((uly - lry)/pixres)

metadata['samples'] = ('%d' % ncols)
metadata['lines'] = ('%d' % nrows)
metadata['map info'][3] = ('%f' % ulx)
metadata['map info'][4] = ('%f' % uly)

junk = envi.write_envi_header(outfile+'.hdr', metadata)
del junk

usethem = np.zeros(len(infiles), dtype=np.int)
## find which files fall within the proposed mosaic bounds
boundring = ogr.Geometry(ogr.wkbLinearRing)
boundring.AddPoint(ulx, uly)
boundring.AddPoint(lrx, uly)
boundring.AddPoint(lrx, lry)
boundring.AddPoint(ulx, lry)
boundring.CloseRings()
bpoly = ogr.Geometry(ogr.wkbPolygon)
bpoly.AddGeometry(boundring)

for i,infile in enumerate(infiles):

  thisring = ogr.Geometry(ogr.wkbLinearRing)
  thisring.AddPoint(filebounds[i][0], filebounds[i][1])
  thisring.AddPoint(filebounds[i][2], filebounds[i][1])
  thisring.AddPoint(filebounds[i][2], filebounds[i][3])
  thisring.AddPoint(filebounds[i][0], filebounds[i][3])
  thisring.CloseRings()

  thispoly = ogr.Geometry(ogr.wkbPolygon)
  thispoly.AddGeometry(thisring)
  result = thispoly.Intersects(bpoly) 
  if result is True:
    usethem[i] = 1

print(usethem)
infiles = np.asarray(infiles)
covered = np.asarray(usethem == 1, dtype=np.bool)
print(infiles[covered])
numused = len(infiles[covered])
filesuse = infiles[covered]

# reduce the file bounds to just those files within the mosaic area.
filebounds = np.asarray(filebounds)[covered,:]

fout = open(indir+outfile, 'wb')

for k in range(0,nrows):
  fullline = np.ndarray(shape=(nbands,ncols), dtype=np.float32)
  reservelines = np.ndarray(shape=(len(filesuse),nbands,ncols), dtype=np.float32)
  score = np.ndarray(shape=(len(filesuse),ncols), dtype=np.float32)

  for j,thisfile in enumerate(filesuse):
    fstartlin = int((filebounds[j,1]-(uly-(k*pixres)))/pixres)
    if (fstartlin < 0):
      # this file not used on this line...skip
      continue

    offsetx = (filebounds[j,0]-ulx)/pixres
    offsety = (uly-filebounds[j,1])/pixres
    fnrows = int((filebounds[j,1]-filebounds[j,3])/pixres)
    fncols = int((filebounds[j,2]-filebounds[j,0])/pixres)

    ## fendlin = int((filebounds[j,3]-lry)/pixres)
    ## if (fendlin < 0):
    ##   fendlin = fnrows - int((ulr-filebounds[j,3])/pixres) - 1
    ## else:
    ##   fendlin = fnrows-1 

    fstartpix = int((filebounds[j,0]-ulx)/pixres)
    if (fstartpix < 0):
      mstart = 0
      fstartpix = abs(fstartpix)
    if (fstartpix >= 0):
      mstart = abs(fstartpix)
      fstartpix = 0

    fendpix = fncols - int((filebounds[j,2]-lrx)/pixres) - 1
    if (fendpix < 0):
      mend = abs(fendpix)
      fendpix = fncols-1
    if (fendpix >= 0):
      mend = ncols-1
      fendpix = abs(fendpix)
  
    data = envi.open(indir+thisfile+'.hdr', indir+thisfile)
    datamm = data.open_memmap(interleave='source', writable=False)

    pdb.set_trace()
    fullline[:,mstart:mend] = datamm[fstartlin,:,fstartpix:fendpix]
    
    score[j,:] = (fullline[3,:] - fullline[2,:])/(fullline[3,:] + fullline[2,:])
    reservelines[j,:,:] = fullline


  ## gone through the files in this line, 
  ## now find the best scores and write out the line
  best = np.argmax(score, axis=0)  
  finalline = reservelines[best,:,:]
  finalline.flatten('F').astype('float32').tofile(fout)

# close the output file
fout.close()
