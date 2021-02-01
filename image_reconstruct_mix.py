#!/bin/env python2
import numpy as np
import gdal, osr
from tempfile import mkdtemp
import os.path as path
import sys
## import pdb

## vswirfile = '/lustre/scratch/cao/dknapp/storage/y17/rb/patch25_test3_rb_img'
## dicamfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch25_20171001_dimac_match'
## hyperfile = 'patch25_20171001_hybrid_rb'

def main(mixfile, dicamfile, maskfile, hyperfile):
  
  ########################################################
  # Open data
  mix = gdal.Open(mixfile)
  dicam = gdal.Open(dicamfile)
  mask = gdal.Open(maskfile)
  
  geotrans = dicam.GetGeoTransform()
  mixmeta = mix.GetMetadata('ENVI') 

  xoff = 0
  yoff = 0
  xcountmix = mix.RasterXSize
  ycountmix = mix.RasterYSize
  xcountmask = mask.RasterXSize
  ycountmask = mask.RasterYSize
  xcountdicam = dicam.RasterXSize
  ycountdicam = dicam.RasterYSize
  
  # Read raster as arrays
  mixdata = mix.ReadAsArray(xoff, yoff, xcountmix, ycountmix).astype(np.float)
  dicamdata = dicam.ReadAsArray(xoff, yoff, xcountdicam, ycountdicam).astype(np.float)
  maskdata = mask.ReadAsArray(xoff, yoff, xcountmask, ycountmask).astype(np.float)

  ## pdb.set_trace()
  #  average dicam data for the RGB bands down to vswir spatial resolution
  dicamcoarse = np.zeros((3,ycountmix,xcountmix), dtype=np.float)
  
  ## red = 45
  ## green = 27
  ## blue = 9
  
  ratio = np.double(10)
  
  for j in range(ycountmix):
    for k in range(xcountmix):
      ## first, find where the shaded data are to avoid
      tempdatared = dicamdata[0,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
        np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]
      
      tempdatagreen = dicamdata[1,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
        np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]
      
      tempdatablue = dicamdata[2,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
        np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]
      
      dicamcoarse[0,j,k] = np.mean(tempdatared)
      dicamcoarse[1,j,k] = np.mean(tempdatagreen)
      dicamcoarse[2,j,k] = np.mean(tempdatablue)

  del tempdatared, tempdatagreen, tempdatablue

  good = np.equal(maskdata, 1)
  numgood = good.sum()
  print "Number of Good pixels: %d" % (numgood)

  roworig, colorig = np.indices(good.shape)
  row = roworig[good]
  col = colorig[good]

  ## pdb.set_trace()

  mixdata = mixdata[:, row, col]
  dicamcoarse = dicamcoarse[:, row, col]

  print "Reshaped arrays"
  print "DiCAM: %d     %d" % dicamcoarse.shape
  print "VSWIR: %d     %d" % mixdata.shape 
  
  GGt = np.linalg.inv(np.matmul(dicamcoarse, dicamcoarse.T))
  B = np.matmul(np.matmul(mixdata, dicamcoarse.T), GGt)
  
  del GGt
  print "Did matrix multiplication"

  ## pdb.set_trace()

  ## create a "checkerboard" mask so that the high resolution data can be ordered in rows 
  ## to match the low re solution data.
  checkers = np.arange(1, (xcountmix*ycountmix)+1).reshape(ycountmix, xcountmix)
  checkers100 = np.kron(checkers, np.ones((10,10))).astype(np.int64)
  goodbig = np.kron(good, np.ones((10,10))).astype(bool)

  checkers100good = checkers100[goodbig]
  sortindex = np.argsort(checkers100good)
  rowbig, colbig = np.indices(goodbig.shape)

  rowbig = rowbig[goodbig].flatten()
  colbig = colbig[goodbig].flatten()
  rowbig = rowbig[sortindex]
  colbig = colbig[sortindex]

  del sortindex, mixdata
  print "Created and sorted Big indices"

  ## pdb.set_trace()

  ## create a numpy memory mapped file, instead of holding array into 

  ## hypercam = np.zeros((52,ycountdicam,xcountdicam), dtype=np.float)
  randnum = ("%06d") % np.random.randint(0,high=100000) 
  tempfile = path.join(mkdtemp(dir='/export/tmp'), randnum+'.dat')
  hypercam = np.memmap(tempfile, dtype='float32', mode='w+', shape=(mix.RasterCount,ycountdicam,xcountdicam))
  hypercam[:, rowbig, colbig] = np.matmul(B, dicamdata[:, rowbig, colbig])
 
  print "Filled Hypercam array"

  # Create for target raster the same projection as for the value raster
  driver = gdal.GetDriverByName('ENVI')
  target_ds = driver.Create(hyperfile, xcountdicam, ycountdicam, mix.RasterCount, gdal.GDT_Float32)
  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt(mix.GetProjectionRef())
  target_ds.SetProjection(raster_srs.ExportToWkt())
  target_ds.SetGeoTransform(geotrans)
  ## target_ds.SetMetadataItem('wavelength_units', vswirmeta['wavelength_units'], 'ENVI') 
  ## target_ds.SetMetadataItem('wavelength', vswirmeta['wavelength'], 'ENVI') 

  for c in range(mix.RasterCount):
    target_ds.GetRasterBand(c+1).WriteArray(hypercam[c,:,:])
    print("Finished band %d of %d" % (c+1, mix.RasterCount))
  
  del target_ds
  del mix, dicam, hypercam

  ## remove temporary directory and file
  try:
    shutil.rmtree(os.path.dirname(tempfile))
  except:
    pass


if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print "[ ERROR ] you must supply 4 arguments: image_reconstruct_mix.py mix dimacimage maskimage fusedimage"
    print "where:"
    print "    mix = an orthocorrected mix image from Benthos"
    print "    dimacimage = an orthocorrected DiMAC image with 3 bands (RGB)"
    print "    maskimage = an orthocorrected mask of the VSWIR image dimensions with 1 beinbg good"
    print "    fusedimage = the fused image of high-resolution data with the bands of mix data."
    print ""

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
