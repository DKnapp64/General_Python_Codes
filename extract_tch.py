#!/bin/env python3
import os, sys
import gdal, ogr, osr
import pyproj
import numpy as np
import pygeos
import math
import glob
from scipy import stats

def main(inshp, outtxt):

  ## create array of 12 offsets to get a 25-meter diameter circle around each
  ## center point
  circpnts1 = np.zeros((25,25), dtype=np.bool)
  centx = 11.5; centy = 11.5;
  for i in np.arange(0.5,25.5,1): 
    for j in np.arange(0.5,25.5,1):
      dist = math.sqrt(np.power(centx-j,2) + np.power(centy-i,2))
      if (dist < 12.5):
        circpnts1[int(i),int(j)] = True

  circpnts2 = np.zeros((13,13), dtype=np.bool)
  centx = 6.5; centy = 6.5;
  for i in np.arange(0.5,12.5,1): 
    for j in np.arange(0.5,12.5,1):
      dist = math.sqrt(np.power(centx-j,2) + np.power(centy-i,2))
      if (dist < 6.25):
        circpnts2[int(i),int(j)] = True

  circpnts3 = np.zeros((50,50), dtype=np.bool)
  centx = 11.5; centy = 24.0;
  for i in np.arange(0.5,50.5,1): 
    for j in np.arange(0.5,50.5,1):
      dist = math.sqrt(np.power(centx-j,2) + np.power(centy-i,2))
      if (dist < 25.0):
        circpnts3[int(i),int(j)] = True

  imglist1 = glob.glob('*_tch_new.tif')                                         
  imglist2 = glob.glob('/data/gdcsdata/Research/Researcher/Heckler/data_delivery/peru_gedi/tch/*.tif')
  imglist = imglist1 + imglist2
  print('Using %d TCH images to compare against.' % (len(imglist)))
  cornarr = np.zeros((len(imglist), 4))

  for k,img in enumerate(imglist):
    tmpDS = gdal.Open(img, gdal.GA_ReadOnly)
    gt = tmpDS.GetGeoTransform()
    ulx = gt[0]
    uly = gt[3]
    lrx = gt[0] + tmpDS.RasterXSize * gt[1]
    lry = gt[3] + tmpDS.RasterYSize * gt[5]
    if (tmpDS.GetProjection() == ''):
      tmpDS = None
      continue
    if math.isclose(gt[1], 1.12, abs_tol=0.01) or math.isclose(gt[1], 0.00, abs_tol=0.01):
      print('Problem image %s: %5.2f resolution.' % (img, gt[1]))
      tmpDS = None
      continue 
    proj = osr.SpatialReference(tmpDS.GetProjection())                          
    utmzone = proj.GetUTMZone()
    if (utmzone < 0):                                                          
      epsgcode = 32700 + abs(utmzone)                                          
    else:                                                                      
      epsgcode = 32600 + utmzone                                               
    try:
      p1 = pyproj.Proj(init='epsg:%5d' % (epsgcode))                                         
    except RuntimeError:
      print('Image %s skipped...no projection' % (img))
      tmpDS = None
      continue
    p2 = pyproj.Proj(init='epsg:3857')                                                     
    ulx1, uly1 = pyproj.transform(p1, p2, ulx, uly )                                  
    lrx1, lry1 = pyproj.transform(p1, p2, lrx, lry )                                  
    cornarr[k,:] = [ulx1, uly1, lrx1, lry1]
    tmpDS = None

  boxarr = pygeos.creation.box(cornarr[:,0], cornarr[:,1], cornarr[:,2], cornarr[:,3])
  print('Finished getting extents of Ground images')

  vecDS = ogr.Open(inshp)                                                     
  lyr = vecDS.GetLayer()                                                        
  lyrdefn = lyr.GetLayerDefn()
  fieldcnt = lyrdefn.GetFieldCount()
  sourceSR = lyr.GetSpatialRef()

  tempfeat = lyr.GetNextFeature()
  tmpgeom = tempfeat.GetGeometryRef()

  lyr.ResetReading()
  
  fout = open(outtxt, 'w')
  ## fout.write('ShotID, ImageName, Res, MeanGRND1, SdevGRND1, ModeGRND1, NGRND1, MeanGRND2, SdevGRND2, ModeGRND2, NGRND2\n')
  fout.write('ShotID, ImageName, Res, FCov1, fCov2, MeanTCH1, SdevTCH1, ModeTCH1, NTCH1, MeanTCH2, SdevTCH2, ModeTCH2, NTCH2\n')

  pseudomerc = pyproj.Proj(init='epsg:3857')

  for feat in lyr:
    geom = feat.GetGeometryRef()
    xc = geom.GetX()
    yc = geom.GetY()
    xcout, ycout = pseudomerc(xc, yc)
    pnt = pygeos.creation.points((xcout, ycout))
    inout = pygeos.predicates.contains(boxarr, pnt)
    shotnum = feat.GetField('SHOT_NUMBE')
    if (np.sum(inout) == 0):
      pnt = None
      continue
    index = np.nonzero(inout)
    covlist = (np.asarray(imglist)[index]).tolist()

    for k,img in enumerate(covlist):
      inDS = gdal.Open(img, gdal.GA_ReadOnly)
      mygt = inDS.GetGeoTransform()
      utmproj = osr.SpatialReference(inDS.GetProjection())
      tcode = utmproj.GetUTMZone()
      if (tcode < 0):
        tcode = 32700 + abs(tcode)
      else:
        tcode = 32600 + tcode
      utmp = pyproj.Proj(init='epsg:%5d' % (tcode))                                         
      xutm, yutm = utmp(xc, yc)
      xoff1 = int(np.floor((xutm - mygt[0])/mygt[1]) - (12./mygt[1]))
      yoff1 = int(np.floor((yutm - mygt[3])/mygt[5]) - abs(12./mygt[5]))
      xoff2 = int(np.floor((xutm - mygt[0])/mygt[1]) - (24.5/mygt[1]))
      yoff2 = int(np.floor((yutm - mygt[3])/mygt[5]) - abs(24.5/mygt[5]))
      ## outsize1 = int(np.floor(12/mygt[1] * 2) + 1)
      ## outsize2 = int(np.floor(24.5/mygt[1] * 2) + 1)
      if (mygt[1] == 1):                                                        
        outsize1 = 25                                                           
        outsize2 = 50                                                           
      elif (mygt[1] == 2):                                                      
        outsize1 = 13                                                           
        outsize2 = 25                                                           
      else:                                                                     
        print('Unfamiliar resolution.')                                         
        inDS = None                                                             
        continue             
      if (((xoff1+outsize1) > inDS.RasterXSize) or ((yoff1+outsize1) > inDS.RasterYSize) \
         or (xoff1 < 0) or (yoff1 < 0)):
        inDS = None
        continue
      if (((xoff2+outsize2) > inDS.RasterXSize) or ((yoff2+outsize2) > inDS.RasterYSize) \
         or (xoff2 < 0) or (yoff2 < 0)):
        inDS = None
        continue
      try:
        data1 = inDS.GetRasterBand(1).ReadAsArray(xoff1, yoff1, outsize1, outsize1)
        data2 = inDS.GetRasterBand(1).ReadAsArray(xoff2, yoff2, outsize2, outsize2)
      except:
        print('Problem getting data from %s' % (img))
        inDS = None
        continue
      if (int(mygt[1]) == 1):
        mydata1 = data1[circpnts1]
        mydata2 = data2[circpnts3]
      if (int(mygt[1]) == 2):
        mydata1 = data1[circpnts2]
        mydata2 = data2[circpnts1]
      good1 = np.logical_and(np.greater(mydata1, -9999), np.less(mydata1, 150.0))
      good2 = np.logical_and(np.greater(mydata2, -9999), np.less(mydata2, 150.0))
      notzero1 = np.not_equal(mydata1, 0)
      notzero2 = np.not_equal(mydata2, 0)
      good1 = np.logical_and(good1, notzero1)
      good2 = np.logical_and(good2, notzero2)
      myn1 = np.sum(good1)
      myn2 = np.sum(good2)
      if (myn1 == 0) or (myn2 == 0):
        inDS = None
        continue
      else:
        fcov1 = 100.0 * np.sum(np.greater_equal(mydata1[good1], 2.0))/float(myn1)
        fcov2 = 100.0 * np.sum(np.greater_equal(mydata2[good2], 2.0))/float(myn2)
        mymean1 = np.mean(mydata1[good1])
        mysdev1 = np.std(mydata1[good1])
        mymode1 = stats.mode(mydata1[good1])[0]
        mymean2 = np.mean(mydata2[good2])
        mysdev2 = np.std(mydata2[good2])
        mymode2 = stats.mode(mydata2[good2])[0]
        fout.write('%18d, %s, %6.2f, %8.1f, %8.1f, %8.2f, %8.2f, %8.2f, %d, %8.2f, %8.2f, %8.2f, %d\n' % (shotnum, img, mygt[1], fcov1, fcov2, mymean1, mysdev1, mymode1, myn1, mymean2, mysdev2, mymode2, myn2))
        inDS = None

  ## close the input and output shapefiles
  vecDS.Destroy()


if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ USAGE ] you must supply 2 arguments: extract_tch.py inshapefile outtext")
    print("")
    sys.exit( 1 )

  main( sys.argv[1], sys.argv[2] )

