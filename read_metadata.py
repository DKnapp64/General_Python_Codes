#!/bin/env python3
import gdal
import numpy as np
import os, sys
import glob
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

## {'aerosol_model': 'continental', 'aot_coverage': 0.5357142857142857, 'aot_mean_quality': 2.6666666666666665, 'aot_method': 'fixed', 'aot_source': 'mod09cma_nrt', 'aot_status': 'Data Found', 'aot_std': 0.050949390521348906, 'aot_used': 0.10160000324249267, 'atmospheric_correction_algorithm': '6Sv2.1', 'atmospheric_model': 'water_vapor_and_ozone', 'luts_version': 3, 'ozone_coverage': 0.5357142857142857, 'ozone_mean_quality': 255.0, 'ozone_method': 'fixed', 'ozone_source': 'mod09cmg_nrt', 'ozone_status': 'Data Found', 'ozone_std': 0.0, 'ozone_used': 0.25, 'satellite_azimuth_angle': 0.0, 'satellite_zenith_angle': 0.0, 'solar_azimuth_angle': 85.50243904924066, 'solar_zenith_angle': 30.09117452557839, 'sr_version': '1.0', 'water_vapor_coverage': 0.5357142857142857, 'water_vapor_mean_quality': 2.6666666666666665, 'water_vapor_method': 'fixed', 'water_vapor_source': 'mod09cma_nrt', 'water_vapor_status': 'Data Found', 'water_vapor_std': 1.4781541107730658, 'water_vapor_used': 3.64066645304362}

def main(startdate, indir, outfile):
  if (os.path.exists(outfile)):
    f = open(outfile, "a")
  else:
    f = open(outfile, "w")
    f.write("FileName, SatID, Instrument, SolarElev, SolarAz, AeroModel, AeroStatus, AeroSDev, AeroUsed, OzStatus, OzSDev, OzUsed, WVStatus, WVSDev, WVUsed\n")

  thefiles = glob.glob(indir+os.path.sep+"2*_3B_AnalyticMS_SR.tif")
  thefiles = sorted(thefiles)
  thedates = []
  for thisdate in thefiles:
    thedates.append(datetime.strptime(os.path.basename(thisdate)[0:8], '%Y%m%d'))

  stdate = datetime.strptime(startdate, '%Y%m%d')
  trimarr = np.array(thefiles)
  mybool = np.asarray([ (d >= stdate) for d in thedates ])
  filestoproc = trimarr[mybool].tolist()
  
  print("Found %d files after start date %s" % (len(filestoproc), startdate))

  for thisfile in filestoproc:
    inDS = gdal.Open(thisfile, gdal.GA_ReadOnly)
    print(thisfile)
    try:
      thedict = eval(inDS.GetMetadata()['TIFFTAG_IMAGEDESCRIPTION'])
    except:
      continue
    if bool(thedict):
      metastuff = thedict['atmospheric_correction']
    else:
      continue
    aeromodel = metastuff['aerosol_model']
    aotstatus = metastuff['aot_status']
    aotstd = metastuff['aot_std']
    aotused = metastuff['aot_used']
    try:
      ozonestatus = metastuff['ozone_status']
      ozonestd = metastuff['ozone_std']
      ozoneused = metastuff['ozone_used']
      waterstatus = metastuff['water_vapor_status']
      waterstd = metastuff['water_vapor_std']
      waterused = metastuff['water_vapor_used']
    except:
      ozonestatus, ozonestd, ozoneused, waterstatus, waterstd, waterused = 'NA', -9, -9, 'NA', -9, -9
  
    parts = thisfile.split('_')
    satid = parts[len(parts)-4]

    xmlfile = os.path.splitext(thisfile)[0][0:-3]+'_metadata.xml'
    if os.path.exists(xmlfile):
      tree = ET.parse(xmlfile)
      root = tree.getroot()
      # get Center coordinate                                                         
      ## pntstring = root[3][0][1][0][0].text                                            
      ## '-155.84954099 20.0185364346'                                                
      ## (loncoord, latcoord) = np.double(pntstring.split())                             
      # get Acquisition Time                                                          
      acqtimestr = root[2][0][3][0][6].text                                           
      acqtype = root[2][0][3][0][6].text                                              
      ## '2018-01-24T21:11:51+00:00'                                                  
      ## get orbit direction                                                          
      orbitDir = root[2][0][3][0][0].text                                             
      ## get solar Azimuth                                                            
      solarAz = np.double(root[2][0][3][0][2].text)                                   
      solarElev = np.double(root[2][0][3][0][3].text)                                 
      ## get apcecraft View angle                                                     
      spacecraftView = np.double(root[2][0][3][0][5].text)
      ## instrument ('PS2' or 'PS2.SD')
      instru = root[2][0][1][0][0].text
    else:
      instru = 'unknown'
      solarElev = -9999.0 
      solarAz = -9999.0 
  
    f.write(("%s, %4s, %s, %6.1f, %6.1f, %s, %s, %7.4f, %7.4f, %s, %7.4f, %7.4f, %s, %7.4f, %7.4f\n") %
       (os.path.basename(thisfile), satid, instru, solarElev, solarAz, aeromodel, aotstatus, aotstd, aotused, ozonestatus, 
        ozonestd, ozoneused, waterstatus, waterstd, waterused))
    inDS = None
  
  f.close()

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ USAGE ] you must supply 3 arguments: read_metadata.py startdate indir outfile")
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3] )

