#!/bin/env python2
import numpy as np
import gdal, osr
import sys

## vswirfile = '/lustre/scratch/cao/dknapp/storage/y17/rb/patch25_test3_rb_img'
## dicamfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch25_20171001_dimac_match'
## hyperfile = 'patch25_20170905_hybrid_rb'

########################################################
# Open data
## red = 45
## green = 27
## blue = 9

def main(vswirfile, dicamfile, hyperfile):
  vswir = gdal.Open(vswirfile)
  dicam = gdal.Open(dicamfile)
  
  geotrans = dicam.GetGeoTransform()
  
  xoff = 0
  yoff = 0
  xcountvswir = vswir.RasterXSize
  ycountvswir = vswir.RasterYSize
  xcountdicam = dicam.RasterXSize
  ycountdicam = dicam.RasterYSize

  vblockSize = 100
  dblockSize = 1000
  numXvBlocks = xcountvswir/vblockSize
  numYvBlocks = ycountvswir/vblockSize
  numXdBlocks = xcountdicam/dblockSize
  numYdBlocks = ycountdicam/dblockSize
  
  hypercam = np.zeros((52, ycountdicam, xcountdicam), dtype=np.float)
  
  ratio = np.double(10)

  # Read raster as arrays
  for ybv in range(numYvBlocks):
    yoffv = ybv * vblockSize - 25
    yoffd = ybv * dblockSize - 250
    vyblock = 150
    dyblock = 1500
    if (yoffd < 0):
      yoffd = 0
      dyblock -= 250
    if (yoffv < 0):
      yoffv = 0
      vyblock -= 25
    if ((yoffv+vyblock) > ycountvswir): 
      vyblock -= 25
    if ((yoffd+dyblock) > ycountdicam): 
      dyblock -= 250
  
    for xbv in range(numXvBlocks):
      xoffv = xbv * vblockSize - 25
      xoffd = xbv * dblockSize - 250
      vxblock = 150
      dxblock = 1500
      if (xoffv < 0): 
        xoffv = 0
        vxblock -= 25
      if (xoffd < 0):
        xoffd = 0
        dxblock -= 250
      if ((xoffv+vxblock) > xcountvswir): 
        vxblock -= 25
      if ((xoffd+dxblock) > xcountdicam): 
        dxblock -= 250
  
      print ("%6d %6d %6d %6d") % (xoffv, yoffv, vxblock, vyblock)
      print ("%6d %6d %6d %6d") % (xoffd, yoffd, dxblock, dyblock)
  
      vswirdata = vswir.ReadAsArray(xoffv, yoffv, vxblock, vyblock).astype(np.float)
      dicamdata = dicam.ReadAsArray(xoffd, yoffd, dxblock, dyblock).astype(np.float)
  
      #  average dicam data for the RGB bands down to vswir spatial resolution
      dicamcoarse = np.zeros((3,vyblock,vxblock), dtype=np.float)
  
      ## dicamcoarse = dicamcoarse.reshape(3, vxblock, vyblock)
      ## dicamcoarse.fill(0)
      ## hypercam.fill(0)
  
      for j in range(np.floor(dyblock/10).astype(int)):
        for k in range(np.floor(dxblock/10).astype(int)):

          ## first, find where the shaded data are to avoid
          tempdatared = dicamdata[0,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
            np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]
          dimacgood1 = np.greater(tempdatared, 85)

          tempdatagreen = dicamdata[1,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
            np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]
          dimacgood2 = np.greater(tempdatagreen, 85)

          tempdatablue = dicamdata[2,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
            np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]
          dimacgood3 = np.greater(tempdatablue, 100)

          dimacgood = np.dstack((dimacgood1, dimacgood2, dimacgood3))
          dimacgood = np.all(dimacgood, axis=2)
  
          if (np.all(np.equal(dimacgood, False))):
            continue

          dicamcoarse[0,j,k] = np.mean(tempdatared[dimacgood])
          dicamcoarse[1,j,k] = np.mean(tempdatagreen[dimacgood])
          dicamcoarse[2,j,k] = np.mean(tempdatablue[dimacgood])

          ## dicamcoarse[0,j,k] = np.mean(dicamdata[0,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
          ##   np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)])
          ## dicamcoarse[1,j,k] = np.mean(dicamdata[1,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
          ##   np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)])
          ## dicamcoarse[2,j,k] = np.mean(dicamdata[2,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
          ##   np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)])
  
      vswirdata = vswirdata.reshape(52, vxblock*vyblock)
      dicamcoarse = dicamcoarse.reshape(3, vxblock*vyblock)

      print ("VSWIR Means: %8.3f %8.3f %8.3f") % (np.mean(vswirdata[44,:]), np.mean(vswirdata[26,:]), np.mean(vswirdata[8,:]))
      print ("DiMAC Means: %8.3f %8.3f %8.3f") % (np.mean(dicamcoarse[0,:]), np.mean(dicamcoarse[26,:]), np.mean(vswirdata[8,:]))
      
      pdb.set_trace()

      GGt = np.linalg.inv(np.matmul(dicamcoarse, dicamcoarse.T))
      B = np.matmul(np.matmul(vswirdata, dicamcoarse.T), GGt)
  
      for t in range(dyblock):
        for w in range(dxblock):
          ## if (w == 999): pdb.set_trace()
          hypercam[:,(yoffd+t),(xoffd+w)] = np.matmul(B, dicamdata[:,t,w])
  
  
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

  if len( sys.argv ) != 4:
    print "[ ERROR ] you must supply 3 arguments: image_reconstruct.py vswirimage dimacimage fusedimage"
    print "where:"
    print "    vswirimage = an orthocorrected VSWIR image with 52 bands of bottom reflectance (Rb)"
    print "    dimacimage = an orthocorrected DiMAC image with 3 bands (RGB)"
    print "    fusedimage = the fused image of high-resolution data with the 52 bands of the VSWIR data."
    print ""

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2], sys.argv[3])
