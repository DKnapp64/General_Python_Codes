#!/bin/env python3
import numpy as np
import sys, os
  
def main(inroot, outputdir):

  rangecoast = np.zeros((2, 256), dtype=np.float32)
  rangeblue = np.zeros((2, 256), dtype=np.float32)
  rangegreen = np.zeros((2, 256), dtype=np.float32)
  rangered = np.zeros((2, 256), dtype=np.float32)
  rangenir = np.zeros((2, 256), dtype=np.float32)
  rangeswir1 = np.zeros((2, 256), dtype=np.float32)
  rangeswir2 = np.zeros((2, 256), dtype=np.float32)

  for lev in np.arange(256):
    inrefl = np.load(outputdir+os.sep+inroot+("_%03d" % lev)+".npy")
    rangecoast[1, lev] = inrefl[0,1] * 10000
    rangeblue[1, lev] = inrefl[1,1] * 10000
    rangegreen[1, lev] = inrefl[2,1] * 10000
    rangered[1, lev] = inrefl[3,1] * 10000
    rangenir[1, lev] = inrefl[4,1] * 10000
    rangeswir1[1, lev] = inrefl[5,1] * 10000
    rangeswir2[1, lev] = inrefl[6,1] * 10000
    rangecoast[0, lev] = inrefl[0,0]
    rangeblue[0, lev] = inrefl[1,0]
    rangegreen[0, lev] = inrefl[2,0]
    rangered[0, lev] = inrefl[3,0]
    rangenir[0, lev] = inrefl[4,0]
    rangeswir1[0, lev] = inrefl[5,0]
    rangeswir2[0, lev] = inrefl[6,0]
  
  np.savez(outputdir+os.sep+inroot+"_luts.npz", rangecoast=rangecoast, rangeblue=rangeblue, rangegreen=rangegreen, \
    rangered=rangered, rangenir=rangenir, rangeswir1=rangeswir1, rangeswir2=rangeswir2)
  print("Done!  Luts saved in " + inroot +"_luts.npz")

  ## remove the unneeded files
  for lev in np.arange(256):
    os.remove(outputdir+os.sep+inroot+("_%03d" % lev)+".npy")

if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ ERROR ] you must supply 2 arguments: assemble_luts.py inroot outputdir")
    print("    inroot = name of input root of the NPY files (e.g, LC08_L1TP_063046_20180606_20180615_01_T1_rad)")
    print("    outputdir = the directory in which output LUT (single *.npz file) will be placed")
    print("")

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2])
