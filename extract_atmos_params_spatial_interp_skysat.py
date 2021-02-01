#!/bin/env python3
import gdal
import osr
import numpy as np
import sys, os
import datetime
import fnmatch, re
import pyproj
from scipy.interpolate import griddata
  
def main(inskysatdir, outparamfile):
  
  inhdfdir = "/Carnegie/DGE/Data/Shared/Labs/Asner/Private/Research/Central_America/Caribbean/modis_atmos_data_for_planet"
  
  filelist = os.listdir(inhdfdir)
  
  skysatroot = '2*_analytic.tif'
  
  skysatregex = fnmatch.translate(skysatroot)
  skysatreobj = re.compile(skysatregex)
  
  skysatlist = []
  
  filelist2 = os.listdir(inskysatdir)
  
  for skysatfile in filelist2:
    gotit = skysatreobj.match(skysatfile)
    if gotit is not None:
      skysatlist.append(skysatfile)
  
  print(("Finished making list of Planet SkySat images: %d" % len(skysatlist)))
  
  paramlist = []
  
  f = open(outparamfile, "w")
  
  for inskysat in skysatlist:
  
    skysatds = gdal.Open(inskysatdir+"/"+inskysat, gdal.GA_ReadOnly)
  
    baseskysat = os.path.basename(inskysat)
    year = int(baseskysat[0:4])
    month = int(baseskysat[4:6])
    day = int(baseskysat[6:8])
    
    imgdate = datetime.date(year, month, day).timetuple().tm_yday
  
    hdfroot = 'MOD08_D3.A' + (("%04d%03d") % (year, imgdate))
    regex = fnmatch.translate(hdfroot + '*.hdf')
    reobj = re.compile(regex)
  
    hdffile = None
  
    for filename in filelist:
      gotit = reobj.match(filename)
      if gotit is not None:
        hdffile = inhdfdir + "/" + filename
        break
    
    if hdffile is None:
      print(("HDF file matching " + hdfroot + " not found for SkySat %s." % (baseskysat)))
      break
    
    print(("HDF file found: %s " % (hdffile)))
    
    modisds = gdal.Open(hdffile, gdal.GA_ReadOnly)
    
    moddatalist = modisds.GetSubDatasets()
    
    aotcard = "Aerosol_Optical_Depth_Average_Ocean_Mean"
    wvcard = "Atmospheric_Water_Vapor_Mean"
    ozcard = "Total_Ozone_Mean"
    
    aotregex = fnmatch.translate(aotcard)
    wvregex = fnmatch.translate(wvcard)
    ozregex = fnmatch.translate(ozcard)
    aotobj = re.compile(aotregex)
    wvobj = re.compile(wvregex)
    ozobj = re.compile(ozregex)
    
    
    for subdataset in moddatalist:
      aotgotit = aotobj.match(subdataset[0].split(':')[4])
      if aotgotit is not None:
        aotsub = subdataset[0]
        break
      
    for subdataset in moddatalist:
      wvgotit = wvobj.match(subdataset[0].split(':')[4])
      if wvgotit is not None:
        wvsub = subdataset[0]
        break
  
    for subdataset in moddatalist:
      ozgotit = ozobj.match(subdataset[0].split(':')[4])
      if ozgotit is not None:
        ozsub = subdataset[0]
        break
    
    aotimg = gdal.Open(aotsub, gdal.GA_ReadOnly).ReadAsArray()
    wvimg = gdal.Open(wvsub, gdal.GA_ReadOnly).ReadAsArray()
    ozimg = gdal.Open(ozsub, gdal.GA_ReadOnly).ReadAsArray()
    
    ## get center lat lon of file
    skysatgt = skysatds.GetGeoTransform()
    ulutmx = skysatgt[0]
    ulutmy = skysatgt[3]
    centerutmx = ulutmx + ((skysatds.RasterXSize/2.) * skysatgt[1])
    centerutmy = ulutmy + ((skysatds.RasterYSize/2.) * skysatgt[5])
    
    projinfo = osr.SpatialReference()
    projinfo.ImportFromWkt(skysatds.GetProjectionRef())
    projutm = pyproj.Proj(projinfo.ExportToProj4())
    centerlonlat = projutm(centerutmx, centerutmy, inverse=True)
    
    ## get pixel and line
    col = np.floor(centerlonlat[0] + 180.0).astype('int')
    row = np.floor(90.0 - centerlonlat[1]).astype('int')
    
    print(("Center Lon/Lat is: %10.5f %10.5f" % (centerlonlat[0], centerlonlat[1])))
    print(("Center Row/Col is: %d %d" % (row, col)))
  
    if (aotimg[1,row,col] == -9999.0):
      print("AOT: missing, need to use interpolated value")
      ## make mask of good data
      good = np.squeeze(np.not_equal(aotimg[1,:,:], -9999.0))
      roworig, colorig = np.indices(good.shape)
      rowgood = roworig[good]
      colgood = colorig[good]
      gridit = griddata(np.column_stack((colgood, rowgood)), aotimg[1,rowgood, colgood].flatten(), (col, row), method='linear').item()
      aotval = gridit/1000.0
    else:
      aotval = aotimg[1,row,col]/1000.0
    
    if (wvimg[row,col] == -9999.0):
      print("WV: missing, need to use interpolated value")
      ## make mask of good data
      good = np.squeeze(np.not_equal(wvimg, -9999.0))
      roworig, colorig = np.indices(good.shape)
      rowgood = roworig[good]
      colgood = colorig[good]
      gridit = griddata(np.column_stack((colgood, rowgood)), wvimg[good].flatten(), (col, row), method='linear').item()
      wvval = gridit/1000.0
    else:
      wvval = wvimg[row,col]/1000.0
    
    if (ozimg[row,col] == -9999.0):
      print("Ozone: missing, need to use interpolated value")
      ## make mask of good data
      good = np.squeeze(np.not_equal(ozimg, -9999.0))
      roworig, colorig = np.indices(good.shape)
      rowgood = roworig[good]
      colgood = colorig[good]
      gridit = griddata(np.column_stack((colgood, rowgood)), ozimg[good].flatten(), (col, row), method='linear').item()
      ozval = gridit/10000.0
    else:
      ozval = ozimg[row,col]/10000.0
    
    print("Extracted Values:")
    print(("AOT: %8.4f    WV: %8.4f   Ozone: %8.4f" % (aotval, wvval, ozval)))
    ## bigstring = "%s, %8.4f, %8.4f, %8.4f" % (baseskysat, aotval, wvval, ozval)
    aotstring = "%8.4f" % (aotval)
    wvstring = "%8.4f" % (wvval)
    ozstring = "%8.4f" % (ozval)
    ## paramlist.append((baseskysat, aotstring, wvstring, ozstring))
    f.write("%s, %8.4f, %8.4f, %8.4f\n" % (baseskysat, aotval, wvval, ozval))
  
    modisds, skysatds = None, None
  
  f.close()
    
if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ ERROR ] you must supply 2 arguments: extract_atmos_params_spatial_interp_skysat.py skysatdir outparamfile")
    print("    skysatdir = directory containing the SkySat images (2*_analytic.tif) to get parameters for.")
    print("    outparamfile = the output CSV file with the SkySat image file name and the AOT, Water Vapor, and Ozone parameters")
    print("")

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2])
