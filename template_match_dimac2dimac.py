#!/bin/env python2
import cv2
from PIL import Image
import numpy as np
import scipy.misc as misc
import gdal, gdalconst
from random import randint
import os, sys
## import pdb

def main(in1, in2, scorethresh, rmsethresh, outf):

  scorethresh = float(scorethresh)
  rmsethresh = float(rmsethresh)

  dimac1ds = gdal.Open(in1)
  dimac2ds = gdal.Open(in2)
  
  ## driver = gdal.GetDriverByName('MEM')
  ## refProj = vswirds.GetProjection()
  ## refTrans = vswirds.GetGeoTransform()
  
  dimacarr1 = np.zeros((dimac1ds.RasterYSize, dimac1ds.RasterXSize, 3), dtype=np.uint8)
  
  bandit = dimac1ds.GetRasterBand(1)
  dimacarr1[:,:,0] = bandit.ReadAsArray() 
  bandit = dimac1ds.GetRasterBand(2)
  dimacarr1[:,:,1] = bandit.ReadAsArray() 
  bandit = dimac1ds.GetRasterBand(3)
  dimacarr1[:,:,2] = bandit.ReadAsArray() 
  
  bandit = None
  dimac1ds = None
  
  dimacarr2 = np.zeros((dimac2ds.RasterYSize, dimac2ds.RasterXSize, 3), dtype=np.uint8)
  
  bandit = dimac2ds.GetRasterBand(1)
  dimacarr2[:,:,0] = bandit.ReadAsArray() 
  bandit = dimac2ds.GetRasterBand(2)
  dimacarr2[:,:,1] = bandit.ReadAsArray() 
  bandit = dimac2ds.GetRasterBand(3)
  dimacarr2[:,:,2] = bandit.ReadAsArray() 
  
  bandit = None
  dimac2ds = None
  
  gray1 = cv2.cvtColor(dimacarr1, cv2.COLOR_BGR2GRAY)
  gray2 = cv2.cvtColor(dimacarr2, cv2.COLOR_BGR2GRAY)

  grayimg1 = Image.fromarray(gray1, mode='L')
  grayimg2 = Image.fromarray(gray2, mode='L')

  tilerows = int(np.floor(dimacarr2.shape[0]/100.)) - 2
  tilecols = int(np.floor(dimacarr2.shape[1]/100.)) - 2

  f = open(outf, 'w')
  f.write("; ENVI Image to Image GCP File\n")
  f.write("; base file: %s\n" % (in2))
  f.write("; warp file: %s\n" % (in1))
  f.write("; Base Image (x,y), Warp Image (x,y)\n")
  f.write(";\n")

  offset = 25

  listpoints = []

  method = eval('cv2.TM_CCOEFF')

  for j in range(tilerows):
    rowrange = (25+(j*100), 25+(j+1)*100)

    for g in range(tilecols):
      colrange = (25+(g*100), 25+(g+1)*100)
  
      ## pdb.set_trace()

      template = gray1[rowrange[0]:rowrange[1],colrange[0]:colrange[1]]
      w, h = template.shape[::-1]
      result = cv2.matchTemplate(gray2, template, method)
      resultsub = result[(rowrange[0]-offset):(rowrange[1]-offset),(colrange[0]-offset):(colrange[1]-offset)]

      minval, maxval, minloc, maxloc = cv2.minMaxLoc(resultsub)
      
      if (maxval > 750000.0):
        tempx = maxloc[0]+(colrange[0]-offset)+25
        tempy = maxloc[1]+(rowrange[0]-offset)+25
        dimac2x = colrange[0]+25
        dimac2y = rowrange[0]+25
        diffx = tempx - dimac2x
        diffy = tempy - dimac2y
        dimac1x = dimac2x - diffx
        dimac1y = dimac2y - diffy
        
        listpoints.append((dimac2x, dimac2y, dimac1x, dimac1y))

        if ((np.abs(dimac2x-dimac1x) < 80) and (np.abs(dimac2y-dimac1y) < 80)):
          f.write(("%10.2f %10.2f " % (dimac2x, dimac2y)) + ("%10.2f %10.2f" % (dimac1x, dimac1y)) + (" %f\n" % maxval))
  
  f.close()

  try:
    os.remove(gray1name)
  except:
    pass  ## if you can't remove it, just skip it
  try:
    os.remove(gray2name)
  except:
    pass

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
      ## f.write(("%10.2f %10.2f " % (inarr1[j,0], inarr1[j,1])) + ("%10.2f %10.2f" % (inarr2[j,0], inarr2[j,1])) + (" %12.2f %12.2f\n" % (dists[j], maxvals[j])))

  f.close()

if __name__ == "__main__":

  if len( sys.argv ) != 6:
    print "[ ERROR ] you must supply 5 arguments: template_match_dimac2dimac.py dimacimage1 dimacimage2 scorethrshold rmsethreshold outputfile"
    print "where:"
    print "    dimacimage1 = an orthocorrected DiMAC image to warp"
    print "    dimacimage2 = an orthocorrected DiMAC image to use as the base"
    print "    scorehreshold = The value of the template matching coefficient threshold BELOW which points are rejected (usually 1000000.0)"
    print "    rmsethreshold = The value of the point RMSE value threshold ABOVE which points are rejected (for DiMAC, usually 30.0)"
    print "    outputfile = an output text file in ENVI image-to-image for warping the first DiMAC image to the second."
    print ""
   
    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] )
