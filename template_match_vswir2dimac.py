#!/bin/env python2
import cv2
from PIL import Image
import numpy as np
import gdal, gdalconst
import os, sys
import time
import random
## import pdb

def main(in1, in2, scorethresh, rmsethresh, outf):

  scorethresh = float(scorethresh)
  rmsethresh = float(rmsethresh)

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
  
  ## find how many Nans are in each band
  numnan1 = np.sum(np.logical_or(np.isnan(vswirarr[:,:,0]), (vswirarr[:,:,0] < -50.0)))
  numnan2 = np.sum(np.logical_or(np.isnan(vswirarr[:,:,1]), (vswirarr[:,:,1] < -50.0)))
  numnan3 = np.sum(np.logical_or(np.isnan(vswirarr[:,:,2]), (vswirarr[:,:,2] < -50.0)))

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
  
  vswir8uint[:,:,0] = cv2.convertScaleAbs(vswirarr[:,:,0], alpha=scale1, beta=shift1)
  vswir8uint[:,:,1] = cv2.convertScaleAbs(vswirarr[:,:,1], alpha=scale2, beta=shift2)
  vswir8uint[:,:,2] = cv2.convertScaleAbs(vswirarr[:,:,2], alpha=scale3, beta=shift3)
  
  bandit = None
   
  temp1 = random.randint(0,100000000)
  temp2 = random.randint(0,100000000)
  nametemp1 = "%010d" % temp1
  nametemp2 = "%010d" % temp2

  gray1 = cv2.cvtColor(vswir8uint, cv2.COLOR_RGB2GRAY)
  grayimg1 = Image.fromarray(gray1, mode='L')
  grayimg1.save(nametemp1+".jpg")
  
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
  grayimg2.save(nametemp2+".jpg")

  tilerows = int(np.floor(dimacarr.shape[0]/20.)) - 2
  tilecols = int(np.floor(dimacarr.shape[1]/20.)) - 2
  
  f = open(outf, 'w')
  f.write("; ENVI Image to Image GCP File\n")
  f.write("; base file: %s\n" % (in2))
  f.write("; warp file: %s\n" % (in1))
  f.write("; Base Image (x,y), Warp Image (x,y)\n")
  f.write(";\n")

  ## offset = 25
  offset = 10

  listpoints = []

  method = eval('cv2.TM_CCOEFF')

  for j in range(tilerows):
    rowrange = (25+j*20, 25+(j+1)*20)

    for g in range(tilecols):
      colrange = (25+g*20, 25+(g+1)*20)

      ## pdb.set_trace()

      template = gray1[rowrange[0]:rowrange[1],colrange[0]:colrange[1]]
      w, h = template.shape[::-1]
      result = cv2.matchTemplate(gray2, template, method)
      resultsub = result[(rowrange[0]-offset):(rowrange[1]-offset),(colrange[0]-offset):(colrange[1]-offset)]

      minval, maxval, minloc, maxloc = cv2.minMaxLoc(resultsub)

      tempx = maxloc[0]+(colrange[0]-offset)+10
      tempy = maxloc[1]+(rowrange[0]-offset)+10
      dimacx = colrange[0]+10
      dimacy = rowrange[0]+10
      diffx = tempx - dimacx
      diffy = tempy - dimacy
      vswirx = dimacx - diffx
      vswiry = dimacy - diffy

      listpoints.append((dimacx, dimacy, vswirx, vswiry))

      ## if ((np.abs(dimac2x-dimac1x) < 80) and (np.abs(dimac2y-dimac1y) < 80)):
      f.write(("%10.2f %10.2f " % (dimacx*10.0, dimacy*10.0)) + ("%10.2f %10.2f" % (vswirx, vswiry)) + (" %f\n" % maxval))


  f.close()

  time.sleep(3.0)
  f = open(outf, 'r')
  listpoints = f.readlines()
  listpoints = listpoints[5:]
  f.close()

  inarr1 = np.array([[float(l.split()[0]), float(l.split()[1]), 0.0] for l in listpoints])
  inarr2 = np.array([[float(l.split()[2]), float(l.split()[3]), 0.0] for l in listpoints])
  maxvals = np.array([[float(l.split()[4])] for l in listpoints])

  n = inarr1.shape[0]

  pad = lambda x:np.hstack([x, np.ones((x.shape[0], 1))])
  unpad = lambda x: x[:,:-1]
  X = pad(inarr1)
  Y = pad(inarr2)
  A, res, rank, s = np.linalg.lstsq(X, Y)
  transform = lambda x: unpad(np.dot(pad(x), A))
  preds = transform(inarr1)
  diffx = preds[:,0] - inarr2[:,0]
  diffy = preds[:,1] - inarr2[:,1]
  dists = np.sqrt(np.power(diffx,2) + np.power(diffy,2))

  rmse = np.sqrt(np.mean(np.power(dists,2)))

  np.savez('testout.npz', inarr1=inarr1, inarr2=inarr2, maxvals=maxvals, dists=dists, rmse=rmse)

  f = open(outf, 'w')
  f.write("; ENVI Image to Image GCP File\n")
  f.write("; base file: %s\n" % (in2))
  f.write("; warp file: %s\n" % (in1))
  f.write("; Base Image (x,y), Warp Image (x,y)\n")
  f.write(";\n")

  for j in range(inarr1.shape[0]):
    if (dists[j] < rmsethresh) and (maxvals[j] > scorethresh):
      f.write(("%10.2f %10.2f " % (inarr1[j,0], inarr1[j,1])) + ("%10.2f %10.2f\n" % (inarr2[j,0], inarr2[j,1])))

  f.close()

  try:
    os.remove(nametemp1+'.jpg')
  except:
    pass

  try:
    os.remove(nametemp2+'.jpg')
  except:
    pass

if __name__ == "__main__":

  if len( sys.argv ) != 6:
    print "[ ERROR ] you must supply 5 arguments: template_match_vswir2dimac.py vswirimage dimacimage scorethrshold rmsethreshold outputfile"
    print "where:"
    print "    vswirimage = an orthocorrected VSWIR image to warp to the DiMAC image"
    print "    dimacimage = an orthocorrected DiMAC image to use as the base"
    print "    scorehreshold = The value of the template matching coefficient threshold BELOW which points are rejected (usually 1000000.0)"
    print "    rmsethreshold = The value of the point RMSE value threshold ABOVE which points are rejected (for DiMAC, usually 30.0)"
    print "    outputfile = an output text file in ENVI image-to-image for warping the first DiMAC image to the second."
    print ""

    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] )
