#!/bin/env python3
import spectral
import spectral.io.envi as envi
import scipy as s
import numpy as np
import os, sys

def main(infile):
  
  inhdr = infile + ".hdr"
  outhdr = os.path.basename(infile)[0:-11] + "_glint900metric.hdr"

  img = envi.open(inhdr, infile)

  wl = s.array([float(w) for w in img.metadata['wavelength']])
  if (wl[0] < 100): 
    wl = wl * 1000
  fwhm = s.array([float(w) for w in img.metadata['fwhm']])

  b900 = s.argmin(abs(wl-900.0))
  ## b1050 = s.argmin(abs(wl-1050.0))
  
  b900imgs = img.read_bands([b900-1, b900, b900+1])
  ## b1050imgs = img.read_bands([b1050-1, b1050, b1050+1])
  
  glintm900 = np.median(b900imgs, axis=2).reshape((b900imgs.shape[0], 1, b900imgs.shape[1]))
  ## glintm1050 = np.median(b1050imgs, axis=2).reshape((b1050imgs.shape[0], 1, b1050imgs.shape[1]))
  
  # make output glint metric file and open memmap
  metadata = img.metadata.copy()
  metadata['bands'] = '%i' % 1
  metadata['interleave'] = 'bil'
  metadata['data type'] = '4'
  out = envi.create_image(outhdr, metadata, ext='',force=True)
  outmm = out.open_memmap(interleave='source', writable=True)

  outmm[:,:,:] = glintm900
  del outmm, out, glintm900, img 
  
  
if __name__ == "__main__":
  
  if len( sys.argv ) != 2:
    print("[ ERROR ] you must supply one argument: input ATREM reflectance file")
    sys.exit( 1 )

  main( sys.argv[1] )
