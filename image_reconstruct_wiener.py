#!/usr/bin/python
import numpy as np
import scipy as s
import gdal, osr
from gdalconst import *

vswirfile = 'north_kailua_patch_rb'
dicamfile = '20170627A_EH021554_patch_bal_ort'
hyperfile = 'north_kailua_hybrid_rb'

########################################################
# Open data
vswir = gdal.Open(vswirfile)
dicam = gdal.Open(dicamfile)

geotrans = dicam.GetGeoTransform()

xoff = 0
yoff = 0
xcountvswir = vswir.RasterXSize
ycountvswir = vswir.RasterYSize
xcountdicam = dicam.RasterXSize
ycountdicam = dicam.RasterYSize

ratio = np.double(2500)/np.double(300)
vswirblock = 300
dimacblock = 2500
dimacbuff = 500
red = 45
green = 27
blue = 9

# Figure out patches
patchcols = np.ceil(xcountvswir/np.double(300.0)).astype(int)
patchrows = np.ceil(ycountvswir/np.double(300.0)).astype(int)

for pcol in range(patchcols):
  for prow in range(patchrows):

    hyperpatchfile = hyperfile + '_%03d_%03d' % (prow, pcol) 

    if (pcol == 0): 
      xvbuff = 0
      xdbuff = 0
    else: 
      xvbuff = np.floor(500.0/ratio).astype(int)
      xdbuff = dimacbuff

    if (prow == 0): 
      yvbuff = 0
      ydbuff = 0
    else: 
      yvbuff = np.floor(500.0/ratio).astype(int)
      ydbuff = dimacbuff

    # Read raster as arrays
    vswirdata = vswir.ReadAsArray(pcol*vswirblock-xvbuff, prow*vswirblock-yvbuff, vswirblock+2*xvbuff, vswirblock+2*yvbuff).astype(np.float)
    dicamdata = dicam.ReadAsArray(np.round(pcol*vswirblock*ratio-xdbuff).astype(np.int), \
      np.round(pcol*vswirblock*ratio-xdbuff).astype(np.int), dimacblock+2*xdbuff, dimacblock+2*ydbuff).astype(np.float)

    # average dicam data for the RGB bands down to vswir spatial resolution
    hypercam = np.zeros((52,dimacblock,dimacblock), dtype=np.float)
    dicamcoarse = np.zeros((10,vswirblock,vswirblock), dtype=np.float)

  for j in range(ycountvswir):
    for k in range(xcountvswir):
      redblock = dicamdata[0,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
                  np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]
      greenblock = dicamdata[1,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
                  np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]
      blueblock = dicamdata[2,np.floor(j*ratio).astype(int):np.floor(j*ratio+ratio).astype(int),\
                  np.floor(k*ratio).astype(int):np.floor(k*ratio+ratio).astype(int)]
      dicamcoarse[0,j,k] = np.mean(redblock)
      dicamcoarse[1,j,k] = np.mean(greenblock)
      dicamcoarse[2,j,k] = np.mean(blueblock)
      dicamcoarse[3,j,k] = np.mean(redblock * greenblock)
      dicamcoarse[4,j,k] = np.mean(redblock * blueblock)
      dicamcoarse[5,j,k] = np.mean(blueblock * greenblock)
      dicamcoarse[6,j,k] = np.mean(redblock * redblock)
      dicamcoarse[7,j,k] = np.mean(greenblock * greenblock)
      dicamcoarse[8,j,k] = np.mean(blueblock * blueblock)
      dicamcoarse[9,j,k] = 1.0

  vswirdata = vswirdata.reshape(52, 300*300)
  dicamcoarse = dicamcoarse.reshape(10, 300*300)
  
  GGt = np.linalg.inv(np.matmul(dicamcoarse, dicamcoarse.T))
  B = np.matmul(np.matmul(vswirdata, dicamcoarse.T), GGt)
  
  for t in range(ycountdicam):
    for w in range(xcountdicam):
      dicampoly = np.array([dicamdata[0,t,w], dicamdata[1,t,w], dicamdata[2,t,w], dicamdata[0,t,w]*dicamdata[1,t,w], \
                              dicamdata[0,t,w]*dicamdata[2,t,w], dicamdata[2,t,w]*dicamdata[1,t,w], \
                              dicamdata[0,t,w]*dicamdata[0,t,w], dicamdata[1,t,w]*dicamdata[1,t,w], \
                              dicamdata[2,t,w]*dicamdata[2,t,w], 1.0])
      hypercam[:,t,w] = np.matmul(B, dicampoly)
  
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
  print("Finished Patch %3d, %3d" % (prow, pcol))

