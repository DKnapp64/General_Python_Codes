#!/bin/env python2
import numpy as np
import gdal, osr
import sys

## vswirfile = '/lustre/scratch/cao/dknapp/storage/y17/rb/patch25_test3_rb_img'
## dicamfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch25_20171001_dimac_match'
## maskfile = 'patch44_20170930_rb_mask'
## hyperfile = 'patch25_20171001_hybrid_rb'

def main(vswirfile, dicamfile, maskfile, hyperfile):
  
  ########################################################
  # Open data
  vswir = gdal.Open(vswirfile)
  dicam = gdal.Open(dicamfile)
  mask = gdal.Open(maskfile)
  
  geotrans = dicam.GetGeoTransform()

  xoff = 0
  yoff = 0
  xcountvswir = vswir.RasterXSize
  ycountvswir = vswir.RasterYSize
  xcountmask = mask.RasterXSize
  ycountmask = mask.RasterYSize
  xcountdicam = dicam.RasterXSize
  ycountdicam = dicam.RasterYSize
  
  # Read raster as arrays
  vswirdata = vswir.ReadAsArray(xoff, yoff, xcountvswir, ycountvswir).astype(np.float)
  dicamdata = dicam.ReadAsArray(xoff, yoff, xcountdicam, ycountdicam).astype(np.float)
  maskdata = mask.ReadAsArray(xoff, yoff, xcountmask, ycountmask).astype(np.uint8)
  
  #  average dicam data for the RGB bands down to vswir spatial resolution
  hypercam = np.zeros((52,ycountdicam,xcountdicam), dtype=np.float)
  dicamcoarse = np.zeros((3,ycountvswir,xcountvswir), dtype=np.float)
  
  ## red = 45
  ## green = 27
  ## blue = 9
  
  ratio = np.double(10)
  
  for j in range(ycountvswir):
    for k in range(xcountvswir):
      ## first, find where the shaded data are to avoid
      tempdatared = dicamdata[0,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
        np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]

      tempdatagreen = dicamdata[1,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
        np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]

      tempdatablue = dicamdata[2,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
        np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]

      orig = np.zeros(3, dtype=np.float)
      orig[0] = np.mean(tempdatared)
      orig[1] = np.mean(tempdatagreen)
      orig[2] = np.mean(tempdatablue)
      bnorig = orig/np.sqrt(np.sum(np.power(orig,2)))  

      dicamcoarse[0,j,k] = bnorig[0]
      dicamcoarse[1,j,k] = bnorig[1]
      dicamcoarse[2,j,k] = bnorig[2]
      del tempdatared, tempdatagreen, tempdatablue

  ## brightness normalize the VSWIR data
  vswirdata = vswirdata.reshape(52, xcountvswir*ycountvswir)
  bnvals = np.sqrt(np.sum(np.power(vswirdata,2), axis=0))
  bnvalsarr = np.dot(np.array([np.ones(52)]).T, bnvals)
  bnvswirdata = vswirdata/bnvalsarr
  bnvswirdata = bnvswirdata.reshape(52, ycountvswir, xcountvswir)

  good = np.equal(maskdata, 1) 
  numgood = good.sum()
  roworig, colorig = np.indices(good.shape)
  row = roworig[good]
  col = colorig[good]

  print "Number of Good pixels: %d" % (numgood)
  dicamcoarse = dicamcoarse[:, row, col]
  bnvswirdata = bnvswirdata[:, row, col]
  ## dicamcoarse = dicamcoarse.reshape(3, numgood)
  
  print "Reshaped arrays"
  print "DiCAM: %d     %d" % dicamcoarse.shape
  print "VSWIR: %d     %d" % bnvswirdata.shape
  
  GGt = np.linalg.inv(np.matmul(dicamcoarse, dicamcoarse.T))
  B = np.matmul(np.matmul(bnvswirdata, dicamcoarse.T), GGt)
  
  for t in range(ycountdicam):
    for w in range(xcountdicam):
      hypercam[:,t,w] = np.matmul(B, dicamdata[:,t,w])
  
  # Create for target raster the same projection as for the value raster
  driver = gdal.GetDriverByName('ENVI')
  target_ds = driver.Create(hyperfile, xcountdicam, ycountdicam, vswir.RasterCount, gdal.GDT_Float32)
  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt(vswir.GetProjectionRef())
  target_ds.SetProjection(raster_srs.ExportToWkt())
  target_ds.SetGeoTransform(geotrans)
  
  for c in range(vswir.RasterCount):
    target_ds.GetRasterBand(c+1).WriteArray(hypercam[c,:,:])
  
  del target_ds
  del vswir, dicam


if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print "[ ERROR ] you must supply 4 arguments: image_reconstruct_whole_brightnorm.py vswirimage dimacimage maskimage fusedimage"
    print "where:"
    print "    vswirimage = an orthocorrected VSWIR image with 52 bands of bottom reflectance (Rb)"
    print "    dimacimage = an orthocorrected DiMAC image with 3 bands (RGB)"
    print "    maskimage = a mask file that is the dimensions of hte VSWSIR image"
    print "    fusedimage = the fused image of high-resolution data with the 52 bands of the VSWIR data."
    print ""

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
