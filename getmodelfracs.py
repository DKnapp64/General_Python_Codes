#!/usr/bin/python
import numpy as np
import scipy as s
import gdal, osr
from gdalconst import *

def getmodelfracs(inx, iny):
  
  centersx = np.load("centersx.npy")
  centersy = np.load("centersy.npy")

  nummods = centersx.shape[0] * centersx.shape[1]

  dists = np.empty(nummods, dtype=float32)

  centersx = centersx.reshape(nummods)
  centersy = centersy.reshape(nummods)

  for j in range(nummods):
    dists[j] = np.sqrt(np.sum(np.power(centersx-inx, 2) + np.power(centersy-iny, 2), axis=0)   
vswirfile = 'north_kailua_patch_rb'
dicamfile = '20170627A_EH021554_patch_bal_ort'
hyperfile = 'north_kailua_hybrid_rb'

########################################################
# Open data
vswir = gdal.Open(vswirfile)
dicam = gdal.Open(dicamfile)

dicamgeotrans = dicam.GetGeoTransform()
vswirgeotrans = vswir.GetGeoTransform()

## >>> dicamgeotrans
## (186054.0, 0.12, 0.0, 2173372.0, 0.0, -0.12)

# Figure out patches
patchcols = np.ceil(xcountvswir/np.double(300.0)).astype(int)
patchrows = np.ceil(ycountvswir/np.double(300.0)).astype(int)

centersx = np.empty((patchrows, patchcols), dtype=float64)
centersy = np.empty((patchrows, patchcols), dtype=float64)

for prow in range(patchrows):
  for pcol in range(patchcols):


    if (pcol == 0): 
      xdbuff = 0
    else: 
      xdbuff = dimacbuff

    if (prow == 0): 
      ydbuff = 0
    else: 
      yvbuff = np.floor(500.0/ratio).astype(int)
      ydbuff = dimacbuff

    centersx[prow, pcol] = dicamgeotrans[0] + (pcol * 2500.0 * dicamgeotrans[1]) + (500.0 * dicamgeotrans[1])
    centersy[prow, pcol] = dicamgeotrans[3] + (prow * 2500.0 * dicamgeotrans[5]) + (500.0 * dicamgeotrans[5])

np.save("centersx.npy", centersx)
np.save("centersy.npy", centersy)

del target_ds
del vswir, dicam

