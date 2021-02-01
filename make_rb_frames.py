#!/bin/env python3
import gdal
import ogr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colorbar as cb
import os, sys
import pyproj
import yaml
import glob
import math

## ascending_20191028_to_20191104/L15-0116E-1153N_br_comp.tif

ascdesc = sys.argv[1]
tileid = sys.argv[2]
shapefile = sys.argv[3]
fid = int(sys.argv[4])

shpDS = ogr.Open(shapefile, 0)
lyr = shpDS.GetLayer()
featcnt = lyr.GetFeatureCount()
projweb = pyproj.Proj('+init=EPSG:3857')                                        

thedirs = glob.glob(ascdesc + '_20[0-9][0-9][0-1][0-9][0-3][0-9]_to_20[0-9][0-9][0-1][0-9][0-3][0-9]')
files = []                                                                      

for thedir in thedirs:
  tilepath = thedir + os.path.sep + tileid + '_br_comp.tif'                     
  if os.path.exists(tilepath):                                                  
    files.append(tilepath)                                                      
                                                                                
files.sort()
print("Got %d files for tile %s" % (len(files), tileid))                        
print("First file: %s" % (files[0]))                                            
print("Last file: %s" % (files[-1]))                                            
                                                                                
## baseline_files = [x for x in files if '201908' not in x and '201909' not in x and '201910' not in x and '201911' not in x]
## bleaching_files = [x for x in files if '201908' in x or '201909' in x or '201910' in x or '201911' in x]

feat = lyr.GetFeature(fid)
geom = feat.GetGeometryRef()                                                
theid = feat.GetField('id')                                                 
near = feat.GetField('NearIsland')                                          
lonlat = geom.GetPoint()                                                    
coordweb = projweb(lonlat[0], lonlat[1])                                    
lonlatstr = '%10.6f, %10.6f' % (lonlat[1], lonlat[0])                       
extentcoords = [coordweb[0]-700.0, coordweb[1]+500.0, coordweb[0]+700.0, coordweb[1]-500.0]

for i in range(len(files)):
  thedate = files[i].split('/')[-2][-8:]
  inDS = gdal.Open(files[i], gdal.GA_ReadOnly)
  gt = inDS.GetGeoTransform()
  extract = [math.floor((extentcoords[0]-gt[0])/gt[1]), math.ceil((extentcoords[1]-gt[3])/gt[5]), 
             math.ceil(1400.0/gt[1]), math.ceil(1000.0/gt[1])]
  rbdata = inDS.GetRasterBand(1).ReadAsArray(extract[0], extract[1], extract[2], extract[3])
  fig = plt.figure(figsize=(10,8))                                            
  fig.suptitle('Hotspot %d from %s' % (theid, thedate))
  ## scale_ax = fig.add_axes([0.5,0.05,0.5,0.02])                             
  ax = fig.add_subplot(111)
  im = ax.imshow(rbdata, cmap='gray', vmin=0.0, vmax=2000.0)                
  norm = mpl.colors.Normalize(vmin=0.0, vmax=2000.0)
  ax.get_xaxis().set_visible(False)                                           
  ax.get_yaxis().set_visible(False)                                           
  cbar_ax = fig.add_axes([0.05,0.05,0.02,0.9])                               
  cb1 = cb.ColorbarBase(cbar_ax, cmap='gray', orientation='vertical', spacing='uniform', norm=norm)
  cb1.set_label('Bottom Refl.', rotation=270)        
  plt.savefig('hotspot%03d_frame%02d.jpg' % (theid, i))
  inDS = None
  plt.close()

shpDS = None
