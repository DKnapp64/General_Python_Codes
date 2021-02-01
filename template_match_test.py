#!/bin/env python2
import cv2
from PIL import Image
## from libtiff import TIFF
import numpy as np
import scipy.misc as misc
import gdal, gdalconst
import os, sys
## import pdb

def main(in1, in2, outf):

  vswirds = gdal.Open(in1)
  vswirarr = np.zeros((vswirds.RasterYSize, vswirds.RasterXSize, 3), dtype=np.float32)
  
  bandit = vswirds.GetRasterBand(45)
  vswirarr[:,:,0] = bandit.ReadAsArray() 
  bandit = vswirds.GetRasterBand(27)
  vswirarr[:,:,1] = bandit.ReadAsArray() 
  bandit = vswirds.GetRasterBand(9)
  vswirarr[:,:,2] = bandit.ReadAsArray() 
  bandit = None
  
  gray1 = np.mean(vswirarr, axis=2)
  grayimg1 = Image.fromarray(gray1, mode='F')
  grayimg1.save("gray1.tif", format='TIFF')

  dimacds = gdal.Open(in2)
  bandit = dimacds.GetRasterBand(1)
  driver = gdal.GetDriverByName('MEM')
  outds = driver.Create('', vswirds.RasterXSize, vswirds.RasterYSize, 3, bandit.DataType)
  refProj = vswirds.GetProjection()
  refTrans = vswirds.GetGeoTransform()
  outds.SetGeoTransform(refTrans)
  outds.SetProjection(refProj)
  
  gdal.ReprojectImage(dimacds, outds, refProj, refProj, gdalconst.GRA_Average)
  
  dimacarr = np.zeros((outds.RasterYSize, outds.RasterXSize, 3), dtype=np.uint8)
  
  bandit = outds.GetRasterBand(1)
  dimacarr[:,:,0] = bandit.ReadAsArray() 
  bandit = outds.GetRasterBand(2)
  dimacarr[:,:,1] = bandit.ReadAsArray() 
  bandit = outds.GetRasterBand(3)
  dimacarr[:,:,2] = bandit.ReadAsArray() 
  
  bandit = None
  dimacds = None
  
  gray2 = cv2.cvtColor(dimacarr, cv2.COLOR_BGR2GRAY)
  grayimg2 = Image.fromarray(gray2, mode='L')
  grayimg2.save('gray2.tif', format='TIFF')
  
  del grayimg1, grayimg2, gray1, gray2

  img1 = cv2.imread("gray1.tif", -1)
  img2 = cv2.imread("gray2.tif", -1)
  imhist,bins = np.histogram(img2.flatten(), 256, normed=True)
  cdf = imhist.cumsum()
  cdf = 255 * cdf / cdf[-1]
  img1byte = misc.bytescale(img1, cmin=0.0, cmax=0.05)
  img1b = np.interp(img1byte.flatten(), bins[:-1], cdf).astype(np.uint8)
  img1b = img1b.reshape(img1.shape)

  method = eval('cv2.TM_CCOEFF')

  tilerows = int(np.floor(img1.shape[0]/50.)) - 2
  tilecols = int(np.floor(img1.shape[1]/50.)) - 2

  f = open(outf, 'w')
  f.write("; ENVI Image to Image GCP File\n")
  f.write("; base file: %s\n" % (in2))
  f.write("; warp file: %s\n" % (in1))
  f.write("; Base Image (x,y), Warp Image (x,y)\n")
  f.write(";\n")

  offset = 25

  for j in range(tilerows):
    rowrange = (25+(j*50), 25+(j+1)*50)

    for g in range(tilecols):
      colrange = (25+(g*50), 25+(g+1)*50)
  
      ## pdb.set_trace()

      template = img1b[rowrange[0]:rowrange[1],colrange[0]:colrange[1]]
      w, h = template.shape[::-1]
      result = cv2.matchTemplate(img2, template, method)
      resultsub = result[(rowrange[0]-offset):(rowrange[1]-offset),(colrange[0]-offset):(colrange[1]-offset)]

      minval, maxval, minloc, maxloc = cv2.minMaxLoc(resultsub)
  
      ## dimacx = colrange[0]+25
      ## dimacy = rowrange[0]+25
      ## vswirx = maxloc[0]+(colrange[0]-offset)+25
      ## vswiry = maxloc[1]+(rowrange[0]-offset)+25
      tempx = maxloc[0]+(colrange[0]-offset)+25
      tempy = maxloc[1]+(rowrange[0]-offset)+25
      dimacx = colrange[0]+25
      dimacy = rowrange[0]+25
      diffx = tempx - dimacx
      diffy = tempy - dimacy
      vswirx = dimacx - diffx
      vswiry = dimacy - diffy
      

      if ((np.abs(dimacx-vswirx) < 8) and (np.abs(dimacy-vswiry) < 8)):
        f.write(("%10.2f %10.2f " % (dimacx * 10, dimacy * 10)) + ("%10.2f %10.2f\n" % (vswirx, vswiry)))
  
  f.close()

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print "[ ERROR ] you must supply 3 arguments: template_match_test.py vswirimage dimacimage outputfile"
    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2], sys.argv[3] )
