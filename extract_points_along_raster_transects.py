#!/bin/env python3
import gdal, ogr
import os, sys
import math
import numpy as np

## transfile = "../GPS/GPS_all_clean_spec_segments_edited_raster.tif"
srfile = "/scratch/dknapp4/Western_Hawaii/Moorea/20190604_moorea_tile_sr.tif"
rbfile = "/scratch/dknapp4/Western_Hawaii/Moorea/20190604_moorea_tile_sr_rb.tif"
depthfile = "/scratch/dknapp4/Western_Hawaii/Moorea/20190604_moorea_tile_sr_depth.tif"
ptsfile = "/scratch/dknapp4/ASD/GPS/GPS_all_clean_asd_points.shp"
## csvfile = "../Spectroscopy/Moorea_all_points_asd_bgr.csv"
outfile = "Moorea_dove_rb_sr_transects_20190710.csv"
asdcsvfile = "/scratch/dknapp4/Spectroscopy/Moorea_Dove_BGR_from_ASD.csv"

asddata = np.genfromtxt(asdcsvfile, dtype=[('fname', 'S43'), ('blue', 'f8'), ('green', 'f8'), ('red', 'f8')], delimiter=',', autostrip=True)

RbDS = gdal.Open(rbfile, gdal.GA_ReadOnly)
Rbblue = RbDS.GetRasterBand(1).ReadAsArray()
Rbgreen = RbDS.GetRasterBand(2).ReadAsArray()
Rbred = RbDS.GetRasterBand(3).ReadAsArray()
## nir = inDS.GetRasterBand(4).ReadAsArray()

SrDS = gdal.Open(srfile, gdal.GA_ReadOnly)
Srblue = SrDS.GetRasterBand(1).ReadAsArray()
Srgreen = SrDS.GetRasterBand(2).ReadAsArray()
Srred = SrDS.GetRasterBand(3).ReadAsArray()
Srnir = SrDS.GetRasterBand(4).ReadAsArray()

depDS = gdal.Open(depthfile, gdal.GA_ReadOnly)
depth = depDS.GetRasterBand(1).ReadAsArray()

gt = SrDS.GetGeoTransform()
gt2 = RbDS.GetGeoTransform()

if np.any(np.not_equal(gt, gt2)):
  print("Extents and Resolution of input images are not equal...stopping")
  rbDS, srDS, depDS = None, None, None
  sys.exit(1)

rbDS, srDS, depDS = None, None, None

pntDS = ogr.GetDriverByName("ESRI Shapefile").Open(ptsfile)
pntlayer = pntDS.GetLayer()
pntCnt = pntlayer.GetFeatureCount()

f = open(outfile, 'w')

for i in range(pntCnt):
  pnt =  pntlayer.GetNextFeature()
  pgeom = pnt.GetGeometryRef()
  xval = pgeom.GetX()
  yval = pgeom.GetY()
  pname = pnt.GetFieldAsString("specname")[0:9]
  ptime = pnt.GetFieldAsString("timepnt")

  ##Get Rb and SR data from Dove
  pixval = int(math.floor((xval - gt[0])/gt[1]))
  linval = int(math.floor((yval - gt[3])/gt[5]))
  dep = depth[linval, pixval]/100.0
  brb = Rbblue[linval, pixval]/10000.0
  grb = Rbgreen[linval, pixval]/10000.0
  rrb = Rbred[linval, pixval]/10000.0
  bsr = Srblue[linval, pixval]/10000.0
  gsr = Srgreen[linval, pixval]/10000.0
  rsr = Srred[linval, pixval]/10000.0
  nsr = Srnir[linval, pixval]/10000.0
  for rec in asddata:
    theasdname = rec['fname'][0:9].decode()
    if (pname == theasdname):
      basd = rec['blue']
      gasd = rec['green']
      rasd = rec['red']
      break

  f.write(("%s, %s, %7.4f, %7.4f, %7.4f, %7.2f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f\n") % (pname, ptime, basd, gasd, rasd, dep, brb, grb, rrb, bsr, gsr, rsr, nsr))
  basd = -9999.0
  gasd = -9999.0
  rasd = -9999.0

f.close()

pntDS = None
