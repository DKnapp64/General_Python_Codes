#!/bin/env python2
import numpy as np
import gdal, osr
## from scipy.signal import argrelextrema, argrelmax
from tempfile import mkdtemp
import os.path as path
import sys
## import pdb

## vswirfile = '/lustre/scratch/cao/dknapp/storage/y17/rb/patch25_test3_rb_img'
## dicamfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch25_20171001_dimac_match'
## hyperfile = 'patch25_20171001_hybrid_rb'

def main(chemfile, dicamfile, maskfile, hyperfile):
  
  ########################################################
  # Open data
  chem = gdal.Open(chemfile)
  dicam = gdal.Open(dicamfile)
  mask = gdal.Open(maskfile)
  
  geotrans = dicam.GetGeoTransform()
  chemmeta = chem.GetMetadata('ENVI') 

  xoff = 0
  yoff = 0
  xcountchem = chem.RasterXSize
  ycountchem = chem.RasterYSize
  xcountmask = mask.RasterXSize
  ycountmask = mask.RasterYSize
  xcountdicam = dicam.RasterXSize
  ycountdicam = dicam.RasterYSize
  
  # Read raster as arrays
  chemdata = chem.ReadAsArray(xoff, yoff, xcountchem, ycountchem).astype(np.float)
  chemdata = chemdata.reshape((1, ycountchem, xcountchem))
  dicamdata = dicam.ReadAsArray(xoff, yoff, xcountdicam, ycountdicam).astype(np.float)
  maskdata = mask.ReadAsArray(xoff, yoff, xcountmask, ycountmask).astype(np.float)
  
  #  average dicam data for the RGB bands down to chem spatial resolution
  dicamcoarse = np.zeros((3, ycountchem, xcountchem), dtype=np.float)
  
  ## red = 45
  ## green = 27
  ## blue = 9
  
  ratio = np.double(10)

  good = np.logical_and(np.equal(maskdata, 1), np.isfinite(chemdata).reshape(maskdata.shape))
  numgood = good.sum()
  print "Number of Good pixels: %d" % (numgood)

  roworig, colorig = np.indices(good.shape)
  row = roworig[good]
  col = colorig[good]

  tempdata = chemdata[:, row, col]
  histo, edges = np.histogram(tempdata, normed=True)
 
  peak = np.argmax(histo)

  for j in range(ycountchem):
    for k in range(xcountchem):
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

  chemdata = chemdata[:, row, col]
  dicamcoarse = dicamcoarse[:, row, col]

  print "Reshaped arrays"
  print "DiCAM: %d     %d" % dicamcoarse.shape
  print "VSWIR: %d     %d" % chemdata.shape 
  
  GGt = np.linalg.inv(np.matmul(dicamcoarse, dicamcoarse.T))
  B = np.matmul(np.matmul(chemdata, dicamcoarse.T), GGt)
  
  randnum = ("%06d") % np.random.randint(0,high=100000) 
  np.save("fusion_matrix_hold_GGt_"+randnum+".npy", GGt)
  np.save("fusion_matrix_hold_B_"+randnum+".npy", B)

  print "Saved matrices to file"
  print "Did matrix multiplication"

  ## create a "checkerboard" mask so that the high resolution data can be ordered in rows 
  ## to match the low resolution data.
  checkers = np.arange(1, (xcountchem*ycountchem)+1).reshape(ycountchem, xcountchem)
  checkers100 = np.kron(checkers, np.ones((10,10))).astype(np.int64)
  goodbig = np.kron(good, np.ones((10,10))).astype(bool)

  checkers100good = checkers100[goodbig]
  sortindex = np.argsort(checkers100good)
  rowbig, colbig = np.indices(goodbig.shape)

  rowbig = rowbig[goodbig].flatten()
  colbig = colbig[goodbig].flatten()
  rowbig = rowbig[sortindex]
  colbig = colbig[sortindex]

  np.save("fusion_matrix_hold_rowbig_"+randnum+".npy", rowbig)
  np.save("fusion_matrix_hold_colbig_"+randnum+".npy", colbig)

  print "Created, sorted and saved Big indices"

  ## Clear some memory
  del chemdata, dicamcoarse
  del rowbig, colbig, GGt

  ## load data in memap mode to conserve memory
  rowbig = np.load("fusion_matrix_hold_rowbig_"+randnum+".npy", mmap_mode='r')
  colbig = np.load("fusion_matrix_hold_colbig_"+randnum+".npy", mmap_mode='r')
  ## GGt = np.load("fusion_matrix_hold_GGt_"+randnum+".npy", mmap_mode='r')
  ## B = np.load("fusion_matrix_hold_B_"+randnum+".npy", mmap_mode='r')

  print "Reloaded data"
  
  numstuff = rowbig.shape[0]
  numchunks = 10
  checksizes = np.zeros((10), dtype=np.int64)
  checksizes[:] = np.floor(numstuff/10.)
  checksizes[-1] += numstuff % 10
  starts = np.roll(checksizes, 1)
  starts[0] = 0
  starts = np.cumsum(starts)
  ends = np.cumsum(checksizes)
  
  ## hypercam = np.zeros((52,ycountdicam,xcountdicam), dtype=np.float)
  tempfile = path.join(mkdtemp(dir='/export/tmp'), randnum+'.dat')
  hypercam = np.memmap(tempfile, dtype='float32', mode='w+', shape=(1,ycountdicam,xcountdicam))

  for nums in np.arange(numchunks):
    rowhold = rowbig[starts[nums]:ends[nums]]
    colhold = colbig[starts[nums]:ends[nums]]
    hypercam[:, rowhold, colhold] = np.matmul(B, dicamdata[:, rowhold, colhold])
    print "Finished chunk %d of %d" % (nums, numchunks)
 
  print "Filled Hypercam array"

  # Create for target raster the same projection as for the value raster
  driver = gdal.GetDriverByName('ENVI')
  target_ds = driver.Create(hyperfile, xcountdicam, ycountdicam, chem.RasterCount, gdal.GDT_Float32, ["INTERLEAVE=BIL"])
  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt(chem.GetProjectionRef())
  target_ds.SetProjection(raster_srs.ExportToWkt())
  target_ds.SetGeoTransform(geotrans)
  ## target_ds.SetMetadataItem('wavelength_units', vswirmeta['wavelength_units'], 'ENVI') 
  ## target_ds.SetMetadataItem('wavelength', vswirmeta['wavelength'], 'ENVI') 

  target_ds.GetRasterBand(1).WriteArray(hypercam[0,:,:])
  
  del target_ds
  del chem, dicam, hypercam

  ## remove temporary directory and file
  try:
    shutil.rmtree(os.path.dirname(tempfile))
  except:
    pass


if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print "[ ERROR ] you must supply 4 arguments: image_reconstruct_chem.py chemimage dimacimage maskimage fusedimage"
    print "where:"
    print "    chemimage = an orthocorrected chem image"
    print "    dimacimage = an orthocorrected DiMAC image with 3 bands (RGB)"
    print "    maskimage = an orthocorrected mask of the chem image dimensions with 1 being good"
    print "    fusedimage = the fused image of high-resolution DiMAC data with the band of chem data."
    print ""

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
