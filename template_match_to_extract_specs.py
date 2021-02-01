#!/bin/env python2
import cv2
from PIL import Image
import numpy as np
import gdal, gdalconst
import ogr
import os, sys
from dbfread import DBF

def get_spectral_wavelengths(inds):
  metalist = inds.GetMetadata_List()
  ## tempwaves = np.zeros(length(metalist)-1, dtype=np.float32)
  tempwaves = []

  for i in np.arange(len(metalist)):
    t1 = metalist[i].split("=")[1].split(" ")[0]
    try:
      t1float = float(t1)
      success = 1
    except:
      success = 0

    if (success == 1):
      tempwaves.append(t1float)

  waves = np.sort(tempwaves)

  return waves

def main(inbasedimac, inshape, invswir, outspecs):

  ## scorethresh = float(scorethresh)
  ## rmsethresh = float(rmsethresh)

  ## reasonable values for Score threshold = 7000
  ## reasonable values for RMSE threshold = 5.0 

  ## def surfit(in1, in2):
  ## in1 = '/lustre/scratch/cao/OahuVSWIRTemp/rad/patch13_20170930_atrem_refl'
  ## in2 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/patch13_20170930_dimac_match'
  ## in1 = '/lustre/scratch/cao/OahuVSWIRTemp/rad/patch4and5_20171001_atrem_refl'
  ## in2 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/patch4and5_20171001_dimac_match'
  ## in1 = '/lustre/scratch/cao/OahuVSWIRTemp/rad/patchHIMB_20171001_atrem_refl3'
  ## in2 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/patchHIMB_20170930_and_20171001_dimac_match'
  ## in1 = '/lustre/scratch/cao/OahuVSWIRTemp/rad/patch42_20170930_atrem_refl'
  ## in2 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/patch42_20170930_dimac_match'
  ## in1 = '/lustre/scratch/cao/OahuVSWIRTemp/rad/patch44_20170930_atrem_refl'
  ## in2 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/patch44_20170930_dimac_match'
  ## in1 = '/lustre/scratch/cao/OahuVSWIRTemp/rad/patch25_20170930_atrem_refl'
  ## in2 = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/patch25_20171001_dimac_match'
  
  table = DBF(os.path.splitext(inshape)[0]+'.dbf', load=True)
  fields = table.field_names

  ## Open up VSWIR image
  vswirds = gdal.Open(invswir)
  vswirarr = np.zeros((vswirds.RasterYSize, vswirds.RasterXSize, 3), dtype=np.float32)
  vswir8uint = np.zeros((vswirds.RasterYSize, vswirds.RasterXSize, 3), dtype=np.uint8)
  
  ## Read in VSWIR bands corresponding to Red, Green, and Blue
  bandit = vswirds.GetRasterBand(45)
  vswirarr[:,:,0] = bandit.ReadAsArray() 
  bandit = vswirds.GetRasterBand(27)
  vswirarr[:,:,1] = bandit.ReadAsArray() 
  bandit = vswirds.GetRasterBand(9)
  vswirarr[:,:,2] = bandit.ReadAsArray() 
  
  ## sort the data to create histograms
  sort1 = np.sort(vswirarr[:,:,0].flatten())
  sort2 = np.sort(vswirarr[:,:,1].flatten())
  sort3 = np.sort(vswirarr[:,:,2].flatten())
  
  ## find how many Nans are in each band
  numnan1 = np.sum(np.logical_or(np.isnan(vswirarr[:,:,0]), (vswirarr[:,:,0] < -50.0)))
  numnan2 = np.sum(np.logical_or(np.isnan(vswirarr[:,:,1]), (vswirarr[:,:,1] < -50.0)))
  numnan3 = np.sum(np.logical_or(np.isnan(vswirarr[:,:,2]), (vswirarr[:,:,2] < -50.0)))

  ## create min, max, and scale factors for each band
  min1 = sort1[np.int(np.floor(0.02 * (len(sort1)-numnan1)))]
  max1 = sort1[np.int(np.floor(0.98 * (len(sort1)-numnan1)))]
  min2 = sort2[np.int(np.floor(0.02 * (len(sort2)-numnan2)))]
  max2 = sort2[np.int(np.floor(0.98 * (len(sort2)-numnan2)))]
  min3 = sort3[np.int(np.floor(0.02 * (len(sort3)-numnan3)))]
  max3 = sort3[np.int(np.floor(0.98 * (len(sort3)-numnan3)))]
  
  scale1 = 255./(max1-min1)
  scale2 = 255./(max2-min2)
  scale3 = 255./(max3-min3)
  shift1 = -(min1*255.)
  shift2 = -(min2*255.)
  shift3 = -(min3*255.)
  
  ## scale VSWIR data to 8-bit
  vswir8uint[:,:,0] = cv2.convertScaleAbs(vswirarr[:,:,0], alpha=scale1, beta=shift1)
  vswir8uint[:,:,1] = cv2.convertScaleAbs(vswirarr[:,:,1], alpha=scale2, beta=shift2)
  vswir8uint[:,:,2] = cv2.convertScaleAbs(vswirarr[:,:,2], alpha=scale3, beta=shift3)
  
  bandit = None
   
  ## create grayscale version of 8-bit VSWIR image
  gray1 = cv2.cvtColor(vswir8uint, cv2.COLOR_RGB2GRAY)
  ## grayimg1 = Image.fromarray(gray1, mode='L')
  ## grayimg1.save(nametemp1+".jpg")
  

  ##
  ## Open up Shapefile and read the points in to an array
  ##
  shpdrv = ogr.GetDriverByName('ESRI Shapefile')
  inshpds = shpdrv.Open(inshape, 0)
  if inshpds is None:
    print 'Could not open file %s' % (inshape)
  else:
    print 'Opened %s' % (inshape)
    layer = inshpds.GetLayer()
    featurecount = layer.GetFeatureCount()
    print "Number of features in %s: %d" % (os.path.basename(inshape), featurecount)
    coords = np.zeros((featurecount, 2), dtype=np.float64)
    for k,feature in enumerate(layer):
      geom = feature.GetGeometryRef()
      coords[k,0] = geom.GetX()
      coords[k,1] = geom.GetY()

  del inshpds, shpdrv 
  

  ##
  ## Open up DiMAC data and read it into memory
  ##
  dimacds = gdal.Open(inbasedimac)
  bandit = dimacds.GetRasterBand(1)
  driver = gdal.GetDriverByName('MEM')
  outds = driver.Create('', vswirds.RasterXSize, vswirds.RasterYSize, 3, bandit.DataType)
  refProj = vswirds.GetProjection()
  vswirgeo = vswirds.GetGeoTransform()
  outds.SetGeoTransform(vswirgeo)
  outds.SetProjection(refProj)

  ## Determine rows and columns of each point in DiMAC and VSWIR
  dimacgeo = dimacds.GetGeoTransform()
  ulxdimac = dimacgeo[0]
  ulydimac = dimacgeo[3]
  resol = dimacgeo[1]
  ulxvswir = vswirgeo[0]
  ulyvswir = vswirgeo[3]
  resolvswir = vswirgeo[1]

  rowcols = np.zeros((featurecount, 2), dtype=np.float64)
  checkrowcols = np.zeros((featurecount, 2), dtype=np.float64)

  for row in np.arange(featurecount):
    rowcols[row,0] = (coords[row,0] - ulxdimac)/resol
    rowcols[row,1] = (ulydimac - coords[row,1])/resol
    checkrowcols[row,0] = (coords[row,0] - ulxvswir)/resolvswir
    checkrowcols[row,1] = (ulyvswir - coords[row,1])/resolvswir
  
  ## Average up DiMAC data to resolution of VSWIR
  gdal.ReprojectImage(dimacds, outds, refProj, refProj, gdalconst.GRA_Average)
  
  method = eval('cv2.TM_CCOEFF')

  rowrange = np.zeros(2, dtype=np.int64)
  colrange = np.zeros(2, dtype=np.int64)

  waves = get_spectral_wavelengths(vswirds)
  wavestring = np.array2string(waves, precision=2, separator=',', max_line_width=100000)
  wavestring = wavestring[1:-1]
  headerstring = ", ".join(fields) + ", "
  headerstring += "Row_VSWIR, Column_VSWIR, Location_Quality, "
  headerstring += wavestring

  f = open(outspecs, 'w')
  f.write("## Input Base Image: %s\n" % (inbasedimac))
  f.write("## Input Spectral Image: %s\n" % (invswir))
  f.write("## Input Shape file: %s\n" % (inshape))
  f.write("## Note: Row and Column numbers are 1-based.\n")
  f.write(headerstring + "\n")

  finalrowcols = np.zeros((featurecount, 2), dtype=np.int64)
  status = []


  for row in np.arange(featurecount):
    startx = np.floor(rowcols[row,0]/10.-20).astype(np.int)
    starty = np.floor(rowcols[row,1]/10.-20).astype(np.int)
    xcount = 41
    ycount = 41
    dimacarr = np.zeros((ycount, xcount, 3), dtype=np.uint8)
    bandit = outds.GetRasterBand(1)
    dimacarr[:,:,0] = bandit.ReadAsArray(startx, starty, xcount, ycount) 
    bandit = outds.GetRasterBand(2)
    dimacarr[:,:,1] = bandit.ReadAsArray(startx, starty, xcount, ycount)
    bandit = outds.GetRasterBand(3)
    dimacarr[:,:,2] = bandit.ReadAsArray(startx, starty, xcount, ycount)
    print "DiMAC Coarse StartX, StartY, xCount, yCount: %d %d %d %d" % (startx, starty, xcount, ycount)
    print "Finished %d" % (row)
  
    bandit = None
    dimacds = None
  
    ## create grayscale version of averaged up DiMAC
    template = cv2.cvtColor(dimacarr, cv2.COLOR_BGR2GRAY)
    ## templateimg = Image.fromarray(template, mode='L')
    ## templateimg.save("template.jpg")

    rowrange[0] = rowcols[row,1]/10. - 40
    rowrange[1] = rowcols[row,1]/10. + 41
    colrange[0] = rowcols[row,0]/10. - 40
    colrange[1] = rowcols[row,0]/10. + 41
  
    vswirsub = gray1[rowrange[0]:rowrange[1], colrange[0]:colrange[1]]
    print "Extraction from VSWIR: X %d %d , Y %d %d" % (colrange[0], colrange[1], rowrange[0], rowrange[1])
  
    ## vswirtomatch = Image.fromarray(vswirsub, mode='L')
    ## vswirtomatch.save("thingtomatchto.tiff")
    ## w, h = template.shape[::-1]
    result = cv2.matchTemplate(vswirsub, template, method)
    ## grayimg3 = Image.fromarray(result, mode='F')
    ## grayimg3.save("result.tiff")
    ## resultsub = result[(rowrange[0]-offset):(rowrange[1]-offset),(colrange[0]-offset):(colrange[1]-offset)]
  
    ## create a simple mask to focus on the center
    donut = np.zeros_like(result, dtype=np.uint8)
    mstartx = int(np.floor(0.25 * (vswirsub.shape[1] - dimacarr.shape[1])))
    mstarty = int(np.floor(0.25 * (vswirsub.shape[0] - dimacarr.shape[0])))
    mstopx = int(np.floor(mstartx + (0.5 * (vswirsub.shape[1] - dimacarr.shape[1]) + 1)))
    mstopy = int(np.floor(mstarty + (0.5 * (vswirsub.shape[0] - dimacarr.shape[0]) + 1)))
    donut[mstarty:mstopy, mstartx:mstopx] = 1
    minval, maxval, minloc, maxloc = cv2.minMaxLoc(result, donut)

    tempx = colrange[0] + 0.5*(vswirsub.shape[1] - dimacarr.shape[1]) + maxloc[0]
    tempy = rowrange[0] + 0.5*(vswirsub.shape[0] - dimacarr.shape[0]) + maxloc[1]

    if (abs(tempx-checkrowcols[row,0]) > 5) or (abs(tempy-checkrowcols[row,1]) > 5):
      status.append("UNCERTAIN MATCH")
    else:
      status.append("OK MATCH")
   
    finalrowcols[row,0] = tempy
    finalrowcols[row,1] = tempx
    ## f.write("%d, %d, %s\n" % (tempx, tempy, status))

    del template, dimacarr, vswirsub, result, donut

  spectra = np.zeros((featurecount, vswirds.RasterCount), dtype=np.float32)
   
  for band in np.arange(vswirds.RasterCount):
    bandit = vswirds.GetRasterBand(band+1)  
    for row in np.arange(featurecount):
      spectra[row, band] = bandit.ReadAsArray(finalrowcols[row,1], finalrowcols[row,0], 1, 1)

  ## Species, Tag, UTMX, UTMY, Lon, Lat,
  for row in np.arange(featurecount):
    stringrecord = ""
    for field in fields:
      stringrecord += "%s, " % str(table.records[row][field])
    stringrecord += "%d, %d, %s, " % (finalrowcols[row,0]+1, finalrowcols[row,1]+1, status[row])
    specrecord = np.array2string(spectra[row,:], precision=6, separator=',', max_line_width=100000)
    f.write(stringrecord + specrecord[1:-1] + "\n")

  f.close()

if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print "[ ERROR ] you must supply 4 arguments: template_match_to_extract_specs.py indimacbase inshape invswir outspecs"
    print "where:"
    print "    indimacbase = an orthocorrected DiMAC image to use as the base"
    print "    inshape = Shape file in the same projection as the DiMAC base image with the points for extracting spectra"
    print "    invswir = an input VSWIR image from which to extract spectra"
    print "    outspecs = The output CSV file with the extracted spectra"
    print ""

    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )
