#!/bin/env python2
import numpy as np
import gdal, osr
import sys

## vswirfile = '/lustre/scratch/cao/dknapp/storage/y17/rb/patch25_test3_rb_img'
## dicamfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch25_20171001_dimac_match'
## hyperfile = 'patch25_20171001_hybrid_rb'

def main(vswirfile, dicamfile, maskfile, hyperfile):
  
  ########################################################
  # Open data
  vswir = gdal.Open(vswirfile)
  dicam = gdal.Open(dicamfile)
  mask = gdal.Open(maskfile)
  
  geotrans = dicam.GetGeoTransform()
  vswirmeta = vswir.GetMetadata('ENVI') 

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
  maskdata = mask.ReadAsArray(xoff, yoff, xcountmask, ycountmask).astype(np.float)
  
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

  vswirdata = vswirdata[:, row, col]
  dicamcoarse = dicamcoarse[:, row, col]
  
  print "Reshaped arrays"
  print "DiCAM: %d     %d" % dicamcoarse.shape
  print "VSWIR: %d     %d" % vswirdata.shape 
  
  GGt = np.linalg.inv(np.matmul(dicamcoarse, dicamcoarse.T))
  B = np.matmul(np.matmul(vswirdata, dicamcoarse.T), GGt)
  
  ## create a "checkerboard" mask so that the high resolution data can be ordered in rows 
  ## to match the low re solution data.
  checkers = np.arange(1, (xcountvswir*ycountvswir)+1).reshape(ycountvswir, xcountvswir)
  checkers100 = np.kron(checkers, np.ones((10,10))).astype(np.int64)
  goodbig = np.kron(good, np.ones((10,10))).astype(bool)

  checkers100good = checkers100[goodbig]
  sortindex = np.argsort(checkers100good)
  rowbig, colbig = np.indices(goodbig.shape)

  rowbig = rowbig[goodbig].flatten()
  colbig = colbig[goodbig].flatten()
  rowbig = rowbig[sortindex]
  colbig = colbig[sortindex]

  hypercam = np.zeros((52,ycountdicam,xcountdicam), dtype=np.float)
  hypercam[:, rowbig, colbig] = np.matmul(B, dicamdata[:, rowbig, colbig])
 
  # Create for target raster the same projection as for the value raster
  driver = gdal.GetDriverByName('ENVI')
  target_ds = driver.Create(hyperfile, xcountdicam, ycountdicam, vswir.RasterCount, gdal.GDT_Float32)
  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt(vswir.GetProjectionRef())
  target_ds.SetProjection(raster_srs.ExportToWkt())
  target_ds.SetGeoTransform(geotrans)
  target_ds.SetMetadataItem('wavelength_units', vswirmeta['wavelength_units'], 'ENVI') 
  target_ds.SetMetadataItem('wavelength', vswirmeta['wavelength'], 'ENVI') 

  for c in range(vswir.RasterCount):
    target_ds.GetRasterBand(c+1).WriteArray(hypercam[c,:,:])
  
  del target_ds
  del vswir, dicam


if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print "[ ERROR ] you must supply 4 arguments: image_reconstruct_whole.py vswirimage dimacimage maskimage fusedimage"
    print "where:"
    print "    vswirimage = an orthocorrected VSWIR image with 52 bands of bottom reflectance (Rb)"
    print "    dimacimage = an orthocorrected DiMAC image with 3 bands (RGB)"
    print "    maskimage = an orthocorrected mask of the VSWIR image dimensions with 1 beinbg good"
    print "    fusedimage = the fused image of high-resolution data with the 52 bands of the VSWIR data."
    print ""

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
