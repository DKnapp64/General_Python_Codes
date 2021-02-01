#!/bin/env python3
from Py6S import *
import numpy as np
import sys, os
  
def main(infile, satnum, levnum, rad1, rad2, rad3, rad4, inaot, inwv, inoz, month, day, hr, lon, lat):

  satnum = int(satnum)

  fileskylist = ['/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat1.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat2.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat3.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat4.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat5.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat6.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat7.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat8.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat9.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat10.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat11.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat12.csv', \
                 '/Carnegie/DGE/caodata/Scratch/dknapp/Data_Cube/RSRs/Skysat_RSR_Skysat13.csv'] 

  specranges = [[0.400, 0.725], [0.400, 0.725], [0.400, 0.750], [0.700, 0.950]]
  data = np.genfromtxt(fileskylist[satnum-1], skip_header=1, delimiter=',', encoding='utf-8')

  data[:,1] = data[:,1]/np.max(data[:,1])
  bluerange = np.arange(specranges[0][0], specranges[0][1]+0.0025, 0.0025)
  bluersr = np.interp(bluerange, data[:,0], data[:,1])

  data[:,2] = data[:,2]/np.max(data[:,2])
  greenrange = np.arange(specranges[1][0], specranges[1][1]+0.0025, 0.0025)
  greenrsr = np.interp(greenrange, data[:,0], data[:,2])

  data[:,3] = data[:,3]/np.max(data[:,3])
  redrange = np.arange(specranges[2][0], specranges[2][1]+0.0025, 0.0025)
  redrsr = np.interp(redrange, data[:,0], data[:,3])

  data[:,4] = data[:,4]/np.max(data[:,4])
  nirrange = np.arange(specranges[3][0], specranges[3][1]+0.0025, 0.0025)
  nirrsr = np.interp(nirrange, data[:,0], data[:,4])

  s_blue = SixS()
  s_blue.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_blue.wavelength = Wavelength(specranges[0][0], specranges[0][1], bluersr)
  
  s_green = SixS()
  s_green.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_green.wavelength = Wavelength(specranges[1][0], specranges[1][1], greenrsr)
  
  s_red = SixS()
  s_red.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_red.wavelength = Wavelength(specranges[2][0], specranges[2][1], redrsr)
  
  s_nir = SixS()
  s_nir.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_nir.wavelength = Wavelength(specranges[3][0], specranges[3][1], nirrsr)
  
  radScaleFactor = 0.01
  
  s_red.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
  s_green.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
  s_blue.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
  s_nir.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
 
  s_red.aot550 = float(inaot)
  s_green.aot550 = float(inaot)
  s_blue.aot550 = float(inaot)
  s_nir.aot550 = float(inaot)

  s_red.geometry = Geometry.Landsat_TM() 
  s_green.geometry = Geometry.Landsat_TM()   
  s_blue.geometry = Geometry.Landsat_TM()     
  s_nir.geometry = Geometry.Landsat_TM()    
  
  s_red.altitudes.set_sensor_satellite_level()
  s_green.altitudes.set_sensor_satellite_level()
  s_blue.altitudes.set_sensor_satellite_level()
  s_nir.altitudes.set_sensor_satellite_level()
  
  s_red.altitudes.set_target_sea_level()
  s_green.altitudes.set_target_sea_level()
  s_blue.altitudes.set_target_sea_level()
  s_nir.altitudes.set_target_sea_level()
  
  s_red.geometry.month = np.int(month)
  s_red.geometry.day = np.int(day)
  s_red.geometry.gmt_decimal_hour = np.float(hr)
  s_red.geometry.latitude = np.float(lat)
  s_red.geometry.longitude = np.float(lon)
 
  s_green.geometry.month = np.int(month)
  s_green.geometry.day = np.int(day)
  s_green.geometry.gmt_decimal_hour = np.float(hr)
  s_green.geometry.latitude = np.float(lat)
  s_green.geometry.longitude = np.float(lon)
 
  s_blue.geometry.month = np.int(month)
  s_blue.geometry.day = np.int(day)
  s_blue.geometry.gmt_decimal_hour = np.float(hr)
  s_blue.geometry.latitude = np.float(lat)
  s_blue.geometry.longitude = np.float(lon)
 
  s_nir.geometry.month = np.int(month)
  s_nir.geometry.day = np.int(day)
  s_nir.geometry.gmt_decimal_hour = np.float(hr)
  s_nir.geometry.latitude = np.float(lat)
  s_nir.geometry.longitude = np.float(lon)

  s_red.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  s_green.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  s_blue.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  s_nir.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  
  s_red.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)
  s_green.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)
  s_blue.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)
  s_nir.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)

  s_blue.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad1))
  s_green.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad2))
  s_red.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad3))
  s_nir.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad4))
  
  mods = [s_blue, s_green, s_red, s_nir]
  
  data = np.zeros(4, dtype=np.float)

  for band in np.arange(4):
    mods[band].run()
    ## mods[band].write_input_file(filename="Example_input_band%1d.txt" % (band+1))
    data[band] = mods[band].outputs.atmos_corrected_reflectance_lambertian
    ## mods[band].outputs.write_output_file("Example_output_band%1d.txt" % (band+1))
     
  np.save(os.path.basename(infile).split('.')[0]+("_%03d" % (np.int(levnum)))+".npy", data)

if __name__ == "__main__":

  if len( sys.argv ) != 16:
    print ("[ ERROR ] you must supply 15 arguments: rad_level_skysat.py infile satnum levnum rad1 rad2 rad3 rad4 inaot inwv inoz month day hr lon lat")
    print ("    infile = name of input image file")
    print ("    satnum = the SkySat satellite number (1-13)")
    print ("    levnum = the squential number of radiance level (0-255)")
    print ("    rad1 = radiance for Blue band at given level")
    print ("    rad2 = radiance for Green band at given level")
    print ("    rad3 = radiance for Red band at given level")
    print ("    rad4 = radiance for NIR band at given level")
    print ("    inaot = input Aerosol Optical Thickness (AOT) at 550nm")
    print ("    inwv = input Water Vapor in cm of precip. water")
    print ("    inoz = input ozone in cm-atm")
    print ("    month = month num (1 through 12)")
    print ("    day = day number")
    print ("    hr = decimal hour in GMT/UTC")
    print ("    lon = approx. longitude at center of image")
    print ("    lat = approx. latitude at center of image")
    print ("")

    sys.exit( 1 )

  main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], \
       sys.argv[12], sys.argv[13], sys.argv[14], sys.argv[15])
