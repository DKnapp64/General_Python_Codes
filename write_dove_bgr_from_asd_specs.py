#!/bin/env python3
import numpy as np
import os, sys
import csv
import re, fnmatch
import spectral

def main(inspeclib, outtxt):
  img = spectral.envi.open(os.path.splitext(inspeclib)[0]+".hdr", inspeclib)
  specs = img.spectra
  specnames = img.names
  
  b400 = np.argmin(abs(np.asarray(img.bands.centers)-400))
  b700 = np.argmin(abs(np.asarray(img.bands.centers)-700))
  
  csvtablefile = "/Carnegie/DGE/caodata/Scratch/dknapp/ASD/Spectroscopy/list_spec_time.txt"
  specrows = []

  with open(csvtablefile, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
      specrows.append(row)

  good = np.zeros(specs.shape[0], dtype=bool)
  bluevals = np.zeros(specs.shape[0], dtype=np.float32) 
  greenvals = np.zeros(specs.shape[0], dtype=np.float32) 
  redvals = np.zeros(specs.shape[0], dtype=np.float32) 

  file0f10 = '/home/dknapp/Dove/planet_dove_spectral_response_0f_10.csv'
  file0c0d = '/home/dknapp/Dove/planet_dove_spectral_response_0c_0d.csv'
  file0e = '/home/dknapp/Dove/planet_dove_spectral_response_0e.csv'
  data0f10 = np.genfromtxt(file0f10, skip_header=1, delimiter=',')
  data0c0d = np.genfromtxt(file0c0d, skip_header=1, delimiter=',')
  data0e = np.genfromtxt(file0e, skip_header=1, delimiter=',')
  datastack = np.stack((data0f10,data0c0d[8:68],data0e), axis=-1)
  meanresp = np.mean(datastack, axis=2)
  respBlue = np.interp(np.arange(400.0, 701.0, 1.0), meanresp[:,0]*1000.0, meanresp[:,1]) 
  respGreen = np.interp(np.arange(400.0, 701.0, 1.0), meanresp[:,0]*1000.0, meanresp[:,2]) 
  respRed = np.interp(np.arange(400.0, 701.0, 1.0), meanresp[:,0]*1000.0, meanresp[:,3]) 

  f = open(outtxt, 'w')
  
  ## red band (650nm) must be greater than blue (400nm) to be considered good
  ## otherwise, sensor must be too far from target to get good reading.
  for i in range(specs.shape[0]):
    root = specnames[i][0:9] + '*'
    myregex = fnmatch.translate(root)
    asdobj = re.compile(myregex)
    for k,asdrow in enumerate(specrows):                                           
      gotit = asdobj.match(asdrow[0])                                              
      if gotit is not None:        
        spectime = asdrow[1]

    thisspec = specs[i,b400:(b700+1)]
    bluevals[i] = np.sum(thisspec * respBlue)/np.sum(respBlue)   
    greenvals[i] = np.sum(thisspec * respGreen)/np.sum(respGreen)   
    redvals[i] = np.sum(thisspec * respRed)/np.sum(respRed)   
    f.write(("%s, %7.4f, %7.4f, %7.4f\n") % (specnames[i], bluevals[i], greenvals[i], redvals[i]))   

  f.close()

if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ ERROR ] you must supply 2 arguments: write_dove_bgr_from_asd_specs.py inspeclib outtxt")
    print("where:")
    print("    inspeclib = the input spectral library")
    print("    outtxt = the output Blue, Green, and Red based on Dove spectral response.")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2] )
