#!/bin/env python3
import gdal
import numpy as np
import matplotlib.pyplot as plt
import sys, os

def close_event():
  plt.close()

# Open data
infiles_vswir = ["chuncho_floodplain_vswir_pca", "chuncho_terrace_vswir_pca",
"cicra_vswir_pca", "costarica_vswir_pca",
"danum_vswir_pca", "ecuador_vswir_pca",
"havo_vswir_pca", "jenaro1_vswir_pca",
"kin_plantation_vswir_pca", "kin_secondforest_vswir_pca",
"kosnipata_vswir_pca", "lapuahoehoe_vswir_pca",
"panama_b3_vswir_pca", "panama_vswir_pca", "puna_vswir_pca"]

infiles_vnir = ["chuncho_floodplain_vnir_pca", "chuncho_terrace_vnir_pca",
"cicra_vnir_pca", "costarica_vnir_pca",
"danum_vnir_pca", "ecuador_vnir_pca",
"havo_vnir_pca", "jenaro1_vnir_pca",
"kin_plantation_vnir_pca", "kin_secondforest_vnir_pca",
"kosnipata_vnir_pca", "lapuahoehoe_vnir_pca",
"panama_b3_vnir_pca", "panama_vnir_pca", "puna_vnir_pca"]

roots = ["chuncho_floodplain", "chuncho_terrace", "cicra", "costarica", "danum", "ecuador",
         "havo", "jenaro1", "kin_plantation", "kin_secondforest", "kosnipata", "laupahoehoe",
         "panama_b3", "panama_canal", "puna"]

thetitles = ["Chuncho Floodplain", "Chuncho Terrace", "CICRA", "Costa Rica", "Danum", "Ecuador",
         "HAVO", "Jenaro", "Kinabatangan Plantation", "Kinabatangan Secondary Forest", "Kosnipata", "Laupahoehoe",
         "Panama Coiba Isl.", "Panama Canal", "Puna"]

infiles_vswir = infiles_vswir[10:]

for j, thefile in enumerate(infiles_vswir):
  rasterDS = gdal.Open(thefile, gdal.GA_ReadOnly)
  for k in range(rasterDS.RasterCount):
    thearray = rasterDS.GetRasterBand(k+1).ReadAsArray()
    good = np.not_equal(thearray, -9999.0)
    ## fig = plt.figure()
    ## timer = fig.canvas.new_timer(interval=2000)
    ## timer.add_callback(close_event)
    plt.suptitle(thetitles[j])
    plt.title(("VSWIR PCA %3d") % (k+1))
    minval = np.percentile(thearray[good], 2)
    maxval = np.percentile(thearray[good], 98)
    plt.imshow(thearray, vmin=minval, vmax=maxval, cmap=plt.get_cmap('Spectral'))
    plt.savefig((roots[j]+"_vswir_%03d.jpg") % (k+1))
    ## timer.start()
    ## plt.show()
    ## fig, timer = None, None
  print(("Finished %s") % (thefile))
  rasterDS = None

for j, thefile in enumerate(infiles_vnir):
  rasterDS = gdal.Open(thefile, gdal.GA_ReadOnly)
  for k in range(rasterDS.RasterCount):
    thearray = rasterDS.GetRasterBand(k+1).ReadAsArray()
    good = np.not_equal(thearray, -9999.0)
    ## fig = plt.figure()
    ## timer = fig.canvas.new_timer(interval=2000)
    ## timer.add_callback(close_event)
    plt.suptitle(thetitles[j])
    plt.title(("VNIR PCA %3d") % (k+1))
    minval = np.percentile(thearray[good], 2)
    maxval = np.percentile(thearray[good], 98)
    plt.imshow(thearray, vmin=minval, vmax=maxval, cmap=plt.get_cmap('Spectral'))
    plt.savefig((roots[j]+"_vnir_%03d.jpg") % (k+1))
    ## timer.start()
    ## plt.show()
    ## fig, timer = None, None
  print(("Finished %s") % (thefile))
  rasterDS = None

