#!/usr/bin/env python2
# David E. Knapp

import os
import sys
import scipy as s
import spectral
import spectral.io.envi as envi

# Return the header associated with an image file
def find_header(imgfile):
  if os.path.exists(imgfile+'.hdr'):
    return imgfile+'.hdr'
  ind = imgfile.rfind('.raw')
  if ind >= 0:
    return imgfile[0:ind]+'.hdr'
  ind = imgfile.rfind('.img')
  if ind >= 0:
    return imgfile[0:ind]+'.hdr'
  raise IOError('No header found for file {0}'.format(imgfile));

def main(in_file):

  # Set up input and output file paths
  in_hdr = find_header(in_file)

  ##########################
  ##  MODIFIY THIS TO GET A BETTER FILENAME
  ##########################
  out_glint_file  = in_file.split('_', 1)[0] +'_glint'
  out_glint_hdr  = in_file.split('_', 1)[0] +'_glint.hdr'

  img = envi.open(in_hdr, in_file)
  inmm = img.open_memmap(interleave='source', writable=False)
  wl = s.array([float(w) for w in img.metadata['wavelength']])
  if (wl[0] < 100): 
    wl = wl * 1000

  fwhm = s.array([float(w) for w in img.metadata['fwhm']])
  if (wl[0] < 100): 
    fwhm = fwhm * 1000

  # set up metadata and constants

  # make output glint file and open memmap
  nl = int(img.metadata['lines'])
  metadata_glint = img.metadata.copy()
  metadata_glint['bands'] = u'1'
  metadata_glint['data type'] = u'4'
  metadata_glint['band names'] = ['Glint at 900nm']
  metadata_glint['interleave'] = 'bsq'
  metadata_glint['description'] = ' make_glint.py from input ATREM reflectance '
  try:
    del metadata_glint['wavelength']
    del metadata_glint['wavelength units']
    del metadata_glint['fwhm']
    del metadata_glint['raw starting band']
    del metadata_glint['raw starting sample']
    del metadata_glint['raw starting line']
    del metadata_glint['line averaging']
  except:
    pass

  out_glint = envi.create_image(out_glint_hdr, metadata_glint, ext='', force=True)
  outmm_glint = out_glint.open_memmap(interleave='source', writable=True)

  # iterate over rows
  start, fin = 0, nl

  for i in range(start, fin):

    Rw = s.array(inmm[i,:,:]) 
    if img.metadata['interleave'] == 'bil':
        Rw = Rw.T
    ## if the ENVI data type is unsigned 16-bit integer, just change it to be signed
    ## so that numpy doesn't interpret them as insanely high numbers (e.g., 65535)
    if int(img.metadata['data type']) == 12:
        Rw.dtype = 'int16'
    if int(img.metadata['data type']) != 4:
        Rw = Rw / s.float32(10000)

    # iterate over columns
    colstart, colfin = 0, img.ncols

    glint_frame = s.zeros((outmm_glint.shape[2],1))

    for col in range(colstart, colfin):

      # check for land and bad data flags
      ## if Rw[col,s.argmin(abs(wl-1000))] > 0.05 or all(Rw[col,:] <= 0):
      if Rw[col,s.argmin(abs(wl-1000))] > 0.10 or all(Rw[col,:] <= 0):
        continue 

      # convert to Rrs 
      Rrs_raw = Rw[col,:] / s.pi

      # subtract glint
      b900 = s.argmin(abs(wl-900.0))
      glint = max(0.0001, s.median(Rrs_raw[(b900-2):(b900+3)]))

      if all(Rrs_raw < 0):
        continue # out of bounds data

      # write output files
      glint_state = glint
      glint_frame[col,0] = glint_state

    outmm_glint[0,i,:]  = glint_frame.reshape(img.ncols)
    if ((i%500) == 0):
      print 'line '+str(i+1)

  del outmm_glint, out_glint, inmm, img


if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print "[ ERROR ] you must supply 1 arguments: make_glint.py inreflfile"
    print "where:"
    print "    inreflfile = a reflectance file in ENVI format"
    print ""

    sys.exit( 1 )

  print main( sys.argv[1] )

