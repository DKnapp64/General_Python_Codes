#!/bin/env python3
import gdal
import osr
import numpy as np
from scipy import interpolate
import sys, os
  
def main(infile, inlutfile, outfile):

  if os.path.isfile(infile): 
    inds = gdal.Open(infile, gdal.GA_ReadOnly)
  else:
    print(("Image File: %s does not exist" % (infile)))
    sys.exit(0)
     
  if os.path.isfile(inlutfile): 
    npzfile = np.load(inlutfile)
  else:
    print(("Lut npz File: %s does not exist" % (inlutfile)))
    sys.exit(0)
     
  rangeblue = npzfile['rangeblue']
  rangegreen = npzfile['rangegreen']
  rangered = npzfile['rangered']
  rangerededge = npzfile['rangerededge']
  rangenir = npzfile['rangenir']

  funclist = []
  funclist.append(interpolate.interp1d(rangeblue[0], rangeblue[1], 'slinear', bounds_error = False, fill_value=(-9999.0, -9999.0), assume_sorted=True))
  funclist.append(interpolate.interp1d(rangegreen[0], rangegreen[1], 'slinear', bounds_error = False, fill_value=(-9999.0, -9999.0), assume_sorted=True))
  funclist.append(interpolate.interp1d(rangered[0], rangered[1], 'slinear', bounds_error = False, fill_value=(-9999.0, -9999.0), assume_sorted=True))
  funclist.append(interpolate.interp1d(rangerededge[0], rangerededge[1], 'slinear', bounds_error = False, fill_value=(-9999.0, -9999.0), assume_sorted=True))
  funclist.append(interpolate.interp1d(rangenir[0], rangenir[1], 'slinear', bounds_error = False, fill_value=(-9999.0, -9999.0), assume_sorted=True))
      
  drv = gdal.GetDriverByName('ENVI')
  outds = drv.Create(outfile, xsize=inds.RasterXSize, ysize=inds.RasterYSize, bands=inds.RasterCount, eType=gdal.GDT_Int16)
  outds.SetProjection(inds.GetProjection())
  outds.SetGeoTransform(inds.GetGeoTransform())
  
  whole = inds.ReadAsArray()
  tot = np.sum(whole, axis=0)
  emptypixels = np.equal(tot, 0)
  del whole, tot
  
  print("Finished Making Mask")
  
  outds.SetMetadataItem('wavelength', "{ 475.0, 540.0, 625.0, 700.0, 800.0 }", 'ENVI')
  outds.SetMetadataItem('wavelength units', "nanometers", 'ENVI')
  outds.SetMetadataItem('data ignore value', "-9999", 'ENVI')
  
  ## run to generate look up tables for range of radiances in each band
  for band in np.arange(inds.RasterCount):
    thisBand = inds.GetRasterBand(int(band+1)).ReadAsArray() * 0.01
    result = np.round(funclist[band](thisBand))
    result[emptypixels] = -9999
    newband = outds.GetRasterBand(int(band+1))
    newband.SetNoDataValue(-9999)
    newband.WriteArray(result)
    del newband
    print("Band %3d is done" % (band+1))
  
  inds = None
  outds = None
  npzfile = None
  
if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ ERROR ] you must supply 3 arguments: apply_refl_lut_rapideye.py inradfile inlutfile outreflfile")
    print("where:")
    print("    inradfile = input Planet radiance image")
    print("    inlutfile = input lutfile iin npz format it must contain 4 arrays with 256 levels")
    print("    outreflfile = atmospherically corrected output surface reflectance image")
    print("")

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2], sys.argv[3])
