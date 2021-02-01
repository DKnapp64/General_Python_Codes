#!/bin/env python3
from Py6S import *
import numpy as np
import sys, os
  
def main(infile, levnum, rad1, rad2, rad3, rad4, rad5, rad6, rad7, inaot, inwv, inoz, month, day, hr, lon, lat):

  s_coast = SixS()
  s_coast.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_coast.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B1)
  s_blue = SixS()
  s_blue.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_blue.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B2)
  s_green = SixS()
  s_green.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_green.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B3)
  s_red = SixS()
  s_red.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_red.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B4)
  s_nir = SixS()
  s_nir.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_nir.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B5)
  s_swir1 = SixS()
  s_swir1.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_swir1.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B6)
  s_swir2 = SixS()
  s_swir2.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_swir2.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B7)
  
  ## radScaleFactor = 0.01
  
  s_coast.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
  s_blue.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
  s_green.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
  s_red.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
  s_nir.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
  s_swir1.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
  s_swir2.atmos_profile = AtmosProfile.UserWaterAndOzone(np.float(inwv), np.float(inoz))
 
  s_coast.aot550 = float(inaot)
  s_blue.aot550 = float(inaot)
  s_green.aot550 = float(inaot)
  s_red.aot550 = float(inaot)
  s_nir.aot550 = float(inaot)
  s_swir1.aot550 = float(inaot)
  s_swir2.aot550 = float(inaot)

  s_coast.geometry = Geometry.Landsat_TM()     
  s_blue.geometry = Geometry.Landsat_TM()     
  s_green.geometry = Geometry.Landsat_TM()   
  s_red.geometry = Geometry.Landsat_TM() 
  s_nir.geometry = Geometry.Landsat_TM()    
  s_swir1.geometry = Geometry.Landsat_TM()    
  s_swir2.geometry = Geometry.Landsat_TM()    
  
  s_coast.altitudes.set_sensor_satellite_level()
  s_blue.altitudes.set_sensor_satellite_level()
  s_green.altitudes.set_sensor_satellite_level()
  s_red.altitudes.set_sensor_satellite_level()
  s_nir.altitudes.set_sensor_satellite_level()
  s_swir1.altitudes.set_sensor_satellite_level()
  s_swir2.altitudes.set_sensor_satellite_level()
  
  s_coast.altitudes.set_target_sea_level()
  s_blue.altitudes.set_target_sea_level()
  s_green.altitudes.set_target_sea_level()
  s_red.altitudes.set_target_sea_level()
  s_nir.altitudes.set_target_sea_level()
  s_swir1.altitudes.set_target_sea_level()
  s_swir2.altitudes.set_target_sea_level()
  
  s_coast.geometry.month = np.int(month)
  s_coast.geometry.day = np.int(day)
  s_coast.geometry.gmt_decimal_hour = np.float(hr)
  s_coast.geometry.latitude = np.float(lat)
  s_coast.geometry.longitude = np.float(lon)
 
  s_blue.geometry.month = np.int(month)
  s_blue.geometry.day = np.int(day)
  s_blue.geometry.gmt_decimal_hour = np.float(hr)
  s_blue.geometry.latitude = np.float(lat)
  s_blue.geometry.longitude = np.float(lon)

  s_green.geometry.month = np.int(month)
  s_green.geometry.day = np.int(day)
  s_green.geometry.gmt_decimal_hour = np.float(hr)
  s_green.geometry.latitude = np.float(lat)
  s_green.geometry.longitude = np.float(lon)
 
  s_red.geometry.month = np.int(month)
  s_red.geometry.day = np.int(day)
  s_red.geometry.gmt_decimal_hour = np.float(hr)
  s_red.geometry.latitude = np.float(lat)
  s_red.geometry.longitude = np.float(lon)
 
  s_nir.geometry.month = np.int(month)
  s_nir.geometry.day = np.int(day)
  s_nir.geometry.gmt_decimal_hour = np.float(hr)
  s_nir.geometry.latitude = np.float(lat)
  s_nir.geometry.longitude = np.float(lon)

  s_swir1.geometry.month = np.int(month)
  s_swir1.geometry.day = np.int(day)
  s_swir1.geometry.gmt_decimal_hour = np.float(hr)
  s_swir1.geometry.latitude = np.float(lat)
  s_swir1.geometry.longitude = np.float(lon)

  s_swir2.geometry.month = np.int(month)
  s_swir2.geometry.day = np.int(day)
  s_swir2.geometry.gmt_decimal_hour = np.float(hr)
  s_swir2.geometry.latitude = np.float(lat)
  s_swir2.geometry.longitude = np.float(lon)

  s_coast.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  s_blue.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  s_green.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  s_red.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  s_nir.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  s_swir1.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  s_swir2.ground_reflectance = GroundReflectance.HomogeneousOcean(6.0, 30.0, 35.0, 0.3)
  
  s_coast.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)
  s_blue.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)
  s_green.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)
  s_red.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)
  s_nir.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)
  s_swir1.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)
  s_swir2.aeroprofile = AeroProfile.PredefinedType(AeroProfile.Maritime)

  s_coast.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad1))
  s_blue.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad2))
  s_green.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad3))
  s_red.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad4))
  s_nir.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad5))
  s_swir1.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad6))
  s_swir2.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(np.float(rad7))
  
  mods = [s_coast, s_blue, s_green, s_red, s_nir, s_swir1, s_swir2]
  
  data = np.zeros((7,2), dtype=np.float)
  radlist = [rad1, rad2, rad3, rad4, rad5, rad6, rad7]
  
  for band in np.arange(7):
    mods[band].run()
    ## mods[band].write_input_file(filename="Example_input_band%1d.txt" % (band+1))
    data[band,1] = mods[band].outputs.atmos_corrected_reflectance_lambertian
    data[band,0] = np.float(radlist[band])
    ## mods[band].outputs.write_output_file("Example_output_band%1d.txt" % (band+1))
     
  np.save(os.path.basename(infile).split('.')[0]+("_%03d" % (np.int(levnum)))+".npy", data)

if __name__ == "__main__":

  if len( sys.argv ) != 18:
    print ("[ ERROR ] you must supply 17 arguments: rad_level.py infile levnum rad1 rad2 rad3 rad4 rad5 rad6 rad7 inaot inwv inoz month day hr lon lat")
    print ("    infile = name of input image file")
    print ("    levnum = the squential number of radiance level (0-255)")
    print ("    rad1 = radiance for Coast band at given level")
    print ("    rad2 = radiance for Blue band at given level")
    print ("    rad3 = radiance for Green band at given level")
    print ("    rad4 = radiance for Red band at given level")
    print ("    rad5 = radiance for NIR band at given level")
    print ("    rad6 = radiance for SWIR1 band at given level")
    print ("    rad7 = radiance for SWIR2 band at given level")
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

  main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], \
       sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], \
       sys.argv[12], sys.argv[13], sys.argv[14], sys.argv[15], sys.argv[16], sys.argv[17])
