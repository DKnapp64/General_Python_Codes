#!/bin/env python2
import cv2
from PIL import Image
import numpy as np
import gdal, gdalconst
import os, sys
## import pdb

def main(in1, in2):

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
  
  vswirds = gdal.Open(in1)
  vswirarr = np.zeros((vswirds.RasterYSize, vswirds.RasterXSize, 3), dtype=np.float32)
  vswir8uint = np.zeros((vswirds.RasterYSize, vswirds.RasterXSize, 3), dtype=np.uint8)
  
  bandit = vswirds.GetRasterBand(45)
  vswirarr[:,:,0] = bandit.ReadAsArray() 
  bandit = vswirds.GetRasterBand(27)
  vswirarr[:,:,1] = bandit.ReadAsArray() 
  bandit = vswirds.GetRasterBand(9)
  vswirarr[:,:,2] = bandit.ReadAsArray() 
  
  
  sort1 = np.sort(vswirarr[:,:,0].flatten())
  sort2 = np.sort(vswirarr[:,:,1].flatten())
  sort3 = np.sort(vswirarr[:,:,2].flatten())
  
  min1 = sort1[np.int(np.floor(0.02 * len(sort1)))]
  max1 = sort1[np.int(np.floor(0.98 * len(sort1)))]
  min2 = sort2[np.int(np.floor(0.02 * len(sort2)))]
  max2 = sort2[np.int(np.floor(0.98 * len(sort2)))]
  min3 = sort3[np.int(np.floor(0.02 * len(sort3)))]
  max3 = sort3[np.int(np.floor(0.98 * len(sort3)))]
  
  scale1 = 255./(max1-min1)
  scale2 = 255./(max2-min2)
  scale3 = 255./(max3-min3)
  shift1 = -(min1*255.)
  shift2 = -(min2*255.)
  shift3 = -(min3*255.)
  
  vswir8uint[:,:,0] = cv2.convertScaleAbs(vswirarr[:,:,0], alpha=scale1, beta=shift1)
  vswir8uint[:,:,1] = cv2.convertScaleAbs(vswirarr[:,:,1], alpha=scale2, beta=shift2)
  vswir8uint[:,:,2] = cv2.convertScaleAbs(vswirarr[:,:,2], alpha=scale3, beta=shift3)
  
  bandit = None
   
  gray1 = cv2.cvtColor(vswir8uint, cv2.COLOR_RGB2GRAY)
  grayimg1 = Image.fromarray(gray1, mode='L')
  grayimg1.save("gray1.jpg")
  
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
  ## img2 = cv2.imread(in2)
  
  gray2 = cv2.cvtColor(dimacarr, cv2.COLOR_BGR2GRAY)
  grayimg2 = Image.fromarray(gray2, mode='L')
  grayimg2.save('gray2.jpg')
  
  ## surf = cv2.xfeatures2d.SURF_create(hessianThreshold=400, nOctaves=4, nOctaveLayers=3, extended=False, upright=False)
  ## sift = cv2.xfeatures2d.SIFT_create(nfeatures=300, contrastThreshold=0.02, sigma=1.0)
  sift = cv2.xfeatures2d.SIFT_create()
  
  kp1, desc1 = sift.detectAndCompute(gray1, None)
  kp2, desc2 = sift.detectAndCompute(gray2, None)
  
  ## Initialize parameters for Flann based matcher
  FLANN_INDEX_KDTREE = 0
  index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
  search_params = dict(checks=50)
  
  ## Initialize the Flann based matcher object
  flann = cv2.FlannBasedMatcher(index_params, search_params)
  
  # Compute the matches
  matches = flann.knnMatch(desc1, desc2, k=2)
  
  print ("Found: %d raw matches") % (len(matches))
  good_matches = []
  
  for m1,m2 in matches:
    if m1.distance < 0.95*m2.distance:
      good_matches.append(m1)
  
  print ("Found: %d good matches at 0.95 distance threshold") % (len(good_matches))
  
  outfilename = os.path.splitext(os.path.basename(in1))[0] + '_' + os.path.splitext(os.path.basename(in2))[0] + '_sift.pts'
  
  f = open(outfilename, 'w')
  f.write("; ENVI Image to Image GCP File\n")
  f.write("; base file: %s\n" % (in2))
  f.write("; warp file: %s\n" % (in1))
  f.write("; Base Image (x,y), Warp Image (x,y)\n")
  f.write(";\n")
  for rec in good_matches:
    f.write("%10.2f %10.2f " % (kp2[rec.trainIdx].pt[0]*10,kp2[rec.trainIdx].pt[1]*10) +\
      "%10.2f %10.2f\n" % (kp1[rec.queryIdx].pt[0], kp1[rec.queryIdx].pt[1]))
  
  f.close()

if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print "[ ERROR ] you must supply two arguments: sift_py_test5.py vswirimage dimacimage"
    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2] )
