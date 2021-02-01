#!/bin/env python3
from Py6S import *
import numpy as np
import sys, os
  
def main(infile, levnum, rad1, rad2, rad3, rad4, inaot, inwv, inoz, month, day, hr, lon, lat):

  s_blue = SixS()
  s_blue.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_blue.wavelength = Wavelength(0.400, 0.725, [ 0.005667, 0.008500, 0.011333, 0.014167, \
  0.017000, 0.013667, 0.010333, 0.007000, 0.003667, 0.004167, 0.004667, 0.005167, 0.005667, \
  0.012833, 0.020000, 0.027167, 0.034333, 0.086500, 0.138667, 0.190833, 0.243000, 0.414167, \
  0.585333, 0.756500, 0.927667, 0.945333, 0.963000, 0.980667, 0.998333, 0.994000, 0.989667, \
  0.985333, 0.981000, 0.965083, 0.949167, 0.933250, 0.917333, 0.889833, 0.862333, 0.834833, \
  0.807333, 0.775417, 0.743500, 0.711583, 0.679667, 0.635250, 0.590833, 0.546417, 0.502000, \
  0.460917, 0.419833, 0.378750, 0.337667, 0.316500, 0.295333, 0.274167, 0.253000, 0.231750, \
  0.210500, 0.189250, 0.168000, 0.151583, 0.135167, 0.118750, 0.102333, 0.094500, 0.086667, \
  0.078833, 0.071000, 0.065833, 0.060667, 0.055500, 0.050333, 0.048583, 0.046833, 0.045083, \
  0.043333, 0.041833, 0.040333, 0.038833, 0.037333, 0.036333, 0.035333, 0.034333, 0.033333, \
  0.033333, 0.033333, 0.033333, 0.033333, 0.034083, 0.034833, 0.035583, 0.036333, 0.038667, \
  0.041000, 0.043333, 0.045667, 0.048917, 0.052167, 0.055417, 0.058667, 0.064917, 0.071167, \
  0.077417, 0.083667, 0.086083, 0.088500, 0.090917, 0.093333, 0.087167, 0.081000, 0.074833, \
  0.068667, 0.062000, 0.055333, 0.048667, 0.042000, 0.032583, 0.023167, 0.013750, 0.004333, \
  0.003250, 0.002167, 0.001083, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
  0.000000])
  
  s_green = SixS()
  s_green.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_green.wavelength = Wavelength(0.400, 0.725, [0.003000, 0.003083, 0.003167, 0.003250, \
  0.003333, 0.003167, 0.003000, 0.002833, 0.002667, 0.002750, 0.002833, 0.002917, 0.003000, \
  0.003417, 0.003833, 0.004250, 0.004667, 0.017417, 0.030167, 0.042917, 0.055667, 0.091500, \
  0.127333, 0.163167, 0.199000, 0.220667, 0.242333, 0.264000, 0.285667, 0.313167, 0.340667, \
  0.368167, 0.395667, 0.423083, 0.450500, 0.477917, 0.505333, 0.538917, 0.572500, 0.606083, \
  0.639667, 0.680167, 0.720667, 0.761167, 0.801667, 0.833250, 0.864833, 0.896417, 0.928000, \
  0.942000, 0.956000, 0.970000, 0.984000, 0.988000, 0.992000, 0.996000, 1.000000, 0.989250, \
  0.978500, 0.967750, 0.957000, 0.939417, 0.921833, 0.904250, 0.886667, 0.864083, 0.841500, \
  0.818917, 0.796333, 0.767667, 0.739000, 0.710333, 0.681667, 0.645000, 0.608333, 0.571667, \
  0.535000, 0.495250, 0.455500, 0.415750, 0.376000, 0.338167, 0.300333, 0.262500, 0.224667, \
  0.206167, 0.187667, 0.169167, 0.150667, 0.141583, 0.132500, 0.123417, 0.114333, 0.111083, \
  0.107833, 0.104583, 0.101333, 0.096500, 0.091667, 0.086833, 0.082000, 0.081417, 0.080833, \
  0.080250, 0.079667, 0.084333, 0.089000, 0.093667, 0.098333, 0.096750, 0.095167, 0.093583, \
  0.092000, 0.087417, 0.082833, 0.078250, 0.073667, 0.057417, 0.041167, 0.024917, 0.008667, \
  0.006667, 0.004667, 0.002667, 0.000667, 0.000500, 0.000333, 0.000167, 0.000000, 0.000000, \
  0.000000])
  
  s_red = SixS()
  s_red.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_red.wavelength = Wavelength(0.400, 0.750, [0.001667, 0.001667, 0.001667, 0.001667, \
  0.001667, 0.001417, 0.001167, 0.000917, 0.000667, 0.000750, 0.000833, 0.000917, 0.001000, \
  0.001000, 0.001000, 0.001000, 0.001000, 0.003000, 0.005000, 0.007000, 0.009000, 0.017667, \
  0.026333, 0.035000, 0.043667, 0.046833, 0.050000, 0.053167, 0.056333, 0.059833, 0.063333, \
  0.066833, 0.070333, 0.067083, 0.063833, 0.060583, 0.057333, 0.059917, 0.062500, 0.065083, \
  0.067667, 0.068333, 0.069000, 0.069667, 0.070333, 0.070000, 0.069667, 0.069333, 0.069000, \
  0.071750, 0.074500, 0.077250, 0.080000, 0.076833, 0.073667, 0.070500, 0.067333, 0.063583, \
  0.059833, 0.056083, 0.052333, 0.052167, 0.052000, 0.051833, 0.051667, 0.057500, 0.063333, \
  0.069167, 0.075000, 0.127250, 0.179500, 0.231750, 0.284000, 0.393167, 0.502333, 0.611500, \
  0.720667, 0.775000, 0.829333, 0.883667, 0.938000, 0.953500, 0.969000, 0.984500, 1.000000, \
  0.997167, 0.994333, 0.991500, 0.988667, 0.987917, 0.987167, 0.986417, 0.985667, 0.973833, \
  0.962000, 0.950167, 0.938333, 0.930250, 0.922167, 0.914083, 0.906000, 0.896917, 0.887833, \
  0.878750, 0.869667, 0.859000, 0.848333, 0.837667, 0.827000, 0.778333, 0.729667, 0.681000, \
  0.632333, 0.563500, 0.494667, 0.425833, 0.357000, 0.278167, 0.199333, 0.120500, 0.041667, \
  0.031833, 0.022000, 0.012167, 0.002333, 0.001833, 0.001333, 0.000833, 0.000333, 0.000250, \
  0.000167, 0.000083, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
  0.000000, 0.000000])
  
  s_nir = SixS()
  s_nir.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
  s_nir.wavelength = Wavelength(0.700, 0.900, [0.004667, 0.003667, 0.002667, 0.001667, \
  0.000667, 0.001083, 0.001500, 0.001917, 0.002333, 0.001833, 0.001333, 0.000833, 0.000333, \
  0.000417, 0.000500, 0.000583, 0.000667, 0.001417, 0.002167, 0.002917, 0.003667, 0.027833, \
  0.052000, 0.076167, 0.100333, 0.259917, 0.419500, 0.579083, 0.738667, 0.795667, 0.852667, \
  0.909667, 0.966667, 0.965333, 0.964000, 0.962667, 0.961333, 0.944917, 0.928500, 0.912083, \
  0.895667, 0.877000, 0.858333, 0.839667, 0.821000, 0.812333, 0.803667, 0.795000, 0.786333, \
  0.770750, 0.755167, 0.739583, 0.724000, 0.714500, 0.705000, 0.695500, 0.686000, 0.669167, \
  0.652333, 0.635500, 0.618667, 0.602833, 0.587000, 0.571167, 0.555333, 0.504917, 0.454500, \
  0.404083, 0.353667, 0.285000, 0.216333, 0.147667, 0.079000, 0.059917, 0.040833, 0.021750, \
  0.002667, 0.002000, 0.001333, 0.000667, 0.000000])
  
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
  
  data = np.zeros((4,2), dtype=np.float)
  radlist = [rad1, rad2, rad3, rad4]

  for band in np.arange(4):
    mods[band].run()
    ## mods[band].write_input_file(filename="Example_input_band%1d.txt" % (band+1))
    data[band,1] = mods[band].outputs.atmos_corrected_reflectance_lambertian
    data[band,0] = np.float(radlist[band])
    ## mods[band].outputs.write_output_file("Example_output_band%1d.txt" % (band+1))
     
  np.save(os.path.basename(infile).split('.')[0]+("_%03d" % (np.int(levnum)))+".npy", data)

if __name__ == "__main__":

  if len( sys.argv ) != 15:
    print ("[ ERROR ] you must supply 14 arguments: rad_level.py infile levnum rad1 rad2 rad3 rad4 inaot inwv inoz month day hr lon lat")
    print ("    infile = name of input image file")
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
       sys.argv[12], sys.argv[13], sys.argv[14])
