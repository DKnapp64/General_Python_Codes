#!/bin/env python3
import numpy as np
import os, sys

def main(redval, greenval, blueval):

  ## calculate water column attenuation index 
  w = greenval - (0.46 * redval) - (0.54 * blueval)

  ## calculate Chl-a (Hu, Lee, and Franz 2012)
  chla = np.float_power(10, (-0.4909 + (191.659*w)))

  print(("Chla: %7.3f") % (chla))


if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ USAGE ] you must supply one argument: chla_qucik.py red green blue")
    print("     red: the red reflectance of deep water (range 0.0-1.0")
    print("     green: the green reflectance of deep water (range 0.0-1.0")
    print("     blue: the blue reflectance of deep water (range 0.0-1.0")
    sys.exit( 0 )

  main( float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]) )
