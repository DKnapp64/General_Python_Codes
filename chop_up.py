#
# David Knapp
#
# Code to break up long flightlines into smaller chunks
# because of benthos.py mempory mapping issues.
#

import os
import sys
import argparse
import spectral
import spectral.io.envi as envi

from ctypes import c_int,c_double


  
def main():

  # parse arguments
  desc = "Break up images into smaller chunks"
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument('input', type=str, metavar='INPUT',
      help='input reflectance file (ENVI header present)')
  args = parser.parse_args()
  s.set_printoptions(precision=4)
  s.seterr(all='ignore')
  scenario = args.scenario

  # Set up input and output file paths
  in_file         = args.input
  in_hdr          = find_header(in_file)

  img = envi.open(in_hdr, in_file)
  envi.read_subregion((0,1), (0,img.shape[1]), use_memmap=False)

  inmm = img.open_memmap(interleave='source', writable=False)
  wl = s.array([float(w) for w in img.metadata['wavelength']])
  if (wl[0] < 100): 
    wl = wl * 1000
  fwhm = s.array([float(w) for w in img.metadata['fwhm']])

  # set up metadata and constants
  const = constants(wl, args.mode, scenario, args.root_dir+'/data/')

  # make output Rb file and open memmap
  nl = int(img.metadata['lines'])
  metadata_Rb = img.metadata.copy()
  metadata_Rb['bands'] = '%i' % sum(const.use_out)
  metadata_Rb['interleave'] = 'bip'
  metadata_Rb['wavelength'] = ['%7.2f'%w for w in wl[const.use_out]]
  metadata_Rb['data type'] = '4'
  out_Rb = envi.create_image(out_Rb_hdr, metadata_Rb, ext='',force=True)
  outmm_Rb = out_Rb.open_memmap(interleave='source', writable=True)

  # make output mixtures file and open memmap
  metadata_mix = img.metadata.copy()
  metadata_mix['bands'] = u'%i'%const.Rb.shape[1]
  metadata_mix['interleave'] = 'bip'
  metadata_mix['band names'] = const.Rb_names
  metadata_mix['data type'] = '4'
  del metadata_mix['wavelength']
  del metadata_mix['fwhm']
  out_mix = envi.create_image(out_mix_hdr, metadata_mix, ext='',force=True)
  outmm_mix = out_mix.open_memmap(interleave='source', writable=True)

  # make output Kd file and open memmap
  metadata_Kd = img.metadata.copy()
  metadata_Kd['bands'] = '%i'%sum(const.use_out)
  metadata_Kd['interleave'] = 'bip'
  metadata_Kd['data type'] = '4'
  metadata_Kd['wavelength'] = ['%7.2f'%w for w in wl[const.use_out]]
  metadata_Kd['fwhm'] = ['%7.2f'%w for w in fwhm[const.use_out]]
  out_Kd = envi.create_image(out_Kd_hdr, metadata_Kd, ext='',force=True)
  outmm_Kd = out_Kd.open_memmap(interleave='source', writable=True)

  # make output bb file and open memmap
  metadata_bb = img.metadata.copy()
  metadata_bb['bands'] = '%i'%sum(const.use_out)
  metadata_bb['interleave'] = 'bip'
  metadata_bb['wavelength'] = ['%7.2f'%w for w in wl[const.use_out]]
  metadata_bb['data type'] = '4'
  out_bb = envi.create_image(out_bb_hdr, metadata_bb, ext='',force=True)
  outmm_bb = out_bb.open_memmap(interleave='source', writable=True)

  # make output depth file and open memmap
  metadata_dep = img.metadata.copy()
  metadata_dep['bands'] =u'1'
  metadata_dep['band names'] = ['Depth (m)']
  metadata_dep['data type'] = '4'
  del metadata_dep['wavelength']
  del metadata_dep['fwhm']
  out_dep = envi.create_image(out_dep_hdr, metadata_dep, ext='',force=True)
  outmm_dep = out_dep.open_memmap(interleave='source', writable=True)

  if args.depth_file is not None:
    bathy = envi.open(args.depth_file+'.hdr', args.depth_file)
    bathymm = bathy.open_memmap(interleave='source', writable=False)
  

  if img.metadata['interleave'] == 'bsq':
    raise IndexError('no BSQ support')
  
  # iterate over rows
  if args.rows is None:
    start, fin = 0, nl
  else:
    start, fin = [int(f) for f in args.rows.split(',')]

  for i in range(start, fin):

    # Flush cache 
    print 'line %i/%i' % (i,nl)

    if args.depth_file is not None:
      del bathy
      bathy= spectral.io.envi.open(args.depth_file+'.hdr', args.depth_file)
      bathymm = bathy.open_memmap(interleave='source', writable=False)
      bath = s.array(bathymm[i,:,:]) 
      if bathy.metadata['interleave'] == 'bil':
          bath = bath.T
    else:
      bath = None

    del img
    img = spectral.io.envi.open(in_hdr, in_file)
    inmm = img.open_memmap(interleave='source', writable=False)
    Rrs = s.array(inmm[i,:,:]) 
    if img.metadata['interleave'] == 'bil':
        Rrs = Rrs.T
    if int(img.metadata['data type']) != 4:
        Rrs = Rrs / s.float32(10000)

    del out_Rb
    out_Rb = spectral.io.envi.open(out_Rb_hdr, out_Rb_file)
    outmm_Rb = out_Rb.open_memmap(interleave='source', writable=True)
    Rb_frame = s.zeros(outmm_Rb.shape[1:])

    del out_Kd
    out_Kd = spectral.io.envi.open(out_Kd_hdr, out_Kd_file)
    outmm_Kd = out_Kd.open_memmap(interleave='source', writable=True)
    Kd_frame = s.zeros(outmm_Kd.shape[1:]) 

    del out_bb
    out_bb = spectral.io.envi.open(out_bb_hdr, out_bb_file)
    outmm_bb = out_bb.open_memmap(interleave='source', writable=True)
    bb_frame = s.zeros(outmm_bb.shape[1:]) 

    del out_dep
    out_dep = spectral.io.envi.open(out_dep_hdr, out_dep_file)
    outmm_dep = out_dep.open_memmap(interleave='source', writable=True)
    dep_frame = s.zeros((outmm_Rb.shape[1],1)) 

    del out_mix
    out_mix = spectral.io.envi.open(out_mix_hdr, out_mix_file)
    outmm_mix = out_mix.open_memmap(interleave='source', writable=True)
    mix_frame = s.zeros(outmm_mix.shape[1:]) 

    # iterate over columns
    if args.columns is None:
      colstart, colfin = 0, img.ncols
    else:
      colstart, colfin = [int(f) for f in args.columns.split(',')]

    for col in range(colstart, colfin):

      if col%100==0:
        print 'column '+str(col)

      # check for land and bad data flags
      if Rrs[col,s.argmin(abs(wl-1000))] > 0.05 or all(Rrs[col,:] <= 0):
         continue 

      # convert to Rrs 
      Rrs_raw = Rrs[col,:] / s.pi

      # subtract glint
      b900 = s.argmin(abs(wl-900.0))
      glint = max(0.0001, s.median(Rrs_raw[(b900-2):(b900+3)]))
      Rrs_raw = Rrs_raw - glint

      if all(Rrs_raw < 0):
         continue # out of bounds data

      # optimize
      arg = (wl, Rrs_raw, const)
      state = init_state(wl, Rrs_raw, const)
      if args.mode != 'aop':
        print("Only AOP retrievals have pure C support")
        state, r = leastsq(err, state, args=arg, xtol=1e-6, ftol=1e-6)
      elif bath is None:
        state, r = c_leastsq_aop(err,state,args=arg,libaop=libaop)
      else:
        b = bath[col,-1]
        state, r = c_leastsq_aop(err,state,args=arg,libaop=libaop,bath=b)

      Rrs_model, Kd, bb, R_b, R_std = forward_rrs(wl, Rrs_raw, state, const, 
        est_sd=True)

      # plot output
      if args.plot:
        print('plotting output')
        err(state, wl, Rrs_raw, const, errbar=None, plot=True)

      # Transform some parameters out of log space, and Chl-a to mg/m^3
      # via the Lee relation
      water_state = state[:const.nwater]
      depth_state = state[const.nwater]
      mix_state   = state[(const.nwater+1):]
      state_phys  = s.r_[water_state, depth_state, mix_state] 
      if const.mode=='iop':
        state_phys[0] = s.exp(s.log(state_phys[0]/0.06)/0.65)

      # text dump
      if args.textout is not None:
        print('writing to '+args.textout)
        with open(args.textout,'w') as f:  
          f.write('#Depth: %6.2f m\n'%depth_state)
          f.write('#wl,Rrs.,model,Rb,Rb_sigma_factor,Kd,bb\n')
          for i in s.where(const.use_out)[0]:
            f.write('%8.6f,%8.6f,%8.6f,%8.6f,%8.6f,%8.6f,%8.6f\n'%\
              (wl[i],Rrs_raw[i],Rrs_model[i],R_b[i],R_std[i],Kd[i],bb[i]))
    
      # write output files
      dep_frame[col,0] = state_phys[const.nbb+const.nKd]
      bb_frame[col,:] = bb[const.use_out]
      Kd_frame[col,:] = Kd[const.use_out]
      Rb_frame[col,:] = R_b[const.use_out]
      mix_frame[col,:] = mix_state

    outmm_Rb[i,:,:]  = Rb_frame
    outmm_Kd[i,:,:]  = Kd_frame
    outmm_bb[i,:,:]  = bb_frame
    outmm_mix[i,:,:]  = mix_frame
    outmm_dep[i,:,:] = dep_frame.T
      
if __name__ == "__main__":
  main()
  #cProfile.run('main()')



