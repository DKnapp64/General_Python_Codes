#!/bin/env python3
import numpy as np
import os, sys
import spectral

def main(inspeclib, outspeclib):
  img = spectral.envi.open(inspeclib+".hdr", inspeclib)
  specs = img.spectra
  
  b400 = np.argmin(abs(np.asarray(img.bands.centers)-400))
  b480 = np.argmin(abs(np.asarray(img.bands.centers)-480))
  b650 = np.argmin(abs(np.asarray(img.bands.centers)-650))
  
  good = np.zeros(specs.shape[0], dtype=bool)
  
  ## red band (650nm) must be greater than blue (400nm) to be considered good
  ## otherwise, sensor must be too far from target to get good reading.
  for i in range(specs.shape[0]):
    if (specs[i,b650] > specs[i,b400]) and (specs[i,b650] > specs[i,b480]):
      good[i] = True
    else:
      good[i] = False
  
  specs = specs[good,:]
  numindex = []
  for g in range(len(good)):
    if (good[g] == True):
      numindex.append(g)
  
  img.spectra = specs
  specnames = img.names
  specnames2 = [specnames[k] for k in numindex]
  img.names = specnames2
  ## create and write out new cleaned library
  img.save(outspeclib, description="cleaned spectral library")

if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ ERROR ] you must supply 2 arguments: proc_moorea_specs.py inspeclib outspeclib")
    print("where:")
    print("    inspeclib = the input spectral library")
    print("    outspeclib = the output specral library with only those spectra that meet criteria")
    print("")

    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2] )

