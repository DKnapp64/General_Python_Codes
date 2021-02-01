import numpy as np
import math

def slopeaspect(win3x3):
  dzdx = ((win3x3[0,2] + (2.0 * win3x3[1,2]) + win3x3[2,2]) \
    - (win3x3[0,0] + (2.0 * win3x3[1,0]) + win3x3[2,0])) / 8.0
  dzdy = ((win3x3[2,0] + (2.0 * win3x3[2,1]) + win3x3[2,2]) \
    - (win3x3[0,0] + (2.0 * win3x3[0,1]) + win3x3[0,2])) / 8.0

  aspect = 57.29578 * np.atan2(dzdy, -dzdx)

  if (aspect < 0):
    cellaspect = 90.0 - aspect
  elif (aspect > 90.0):
    cellaspect = 360.0 - aspect + 90.0
  else:
    cellaspect = 90.0 - aspect

  slope = math.atan(math.sqrt(dzdx**2 + dzdy**2)) * 57.29578
  return (slope, cellaspect)
