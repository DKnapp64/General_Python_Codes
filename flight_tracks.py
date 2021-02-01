import numpy as np
import numpy.matlib
import gdal
from gdalconst import *
import sys
import subprocess
import os



infile = sys.argv[1]
maskfile = sys.argv[2]
outfile = sys.argv[3]
outfile_mask = sys.argv[4]

dataset = gdal.Open(infile,gdal.GA_ReadOnly)
dat = dataset.ReadAsArray()
dat[dat <= 0] = 0
dat[dat > 0] = 255

if (maskfile != 'null'):
    maskset = gdal.Open(maskfile,gdal.GA_ReadOnly)
    mask = maskset.ReadAsArray()
    dat[mask == 0] = 0


driver = gdal.GetDriverByName('ENVI')
driver.Register()
outname = os.path.join('tmp','kmz_tmp')
outDataset = driver.Create(outname,
                           dat.shape[1],dat.shape[0],1,GDT_Byte)
outDataset.SetProjection(dataset.GetProjection())
loc_trans = dataset.GetGeoTransform()

outDataset.SetGeoTransform(loc_trans)
outDataset.GetRasterBand(1).SetNoDataValue(-9999)
outDataset.GetRasterBand(1).WriteArray(dat,0,0)
del outDataset

cmd_str='gdal_translate ' + os.path.join('tmp','kmz_tmp') + ' ' + outfile_mask + '.tif' + ' --config GDAL_CACHEMAX 60000 -co COMPRESS=LZW'
subprocess.call(cmd_str,shell=True)

cmd_str='gdalwarp ' + os.path.join('tmp','kmz_tmp') + ' ' + os.path.join('tmp','kmz_tmp.tif') + ' -t_srs EPSG:4326 -wo NUM_THREADS=20'
subprocess.call(cmd_str,shell=True)

cmd_str='python gdal_polygonize.py -mask ' + os.path.join('tmp','kmz_tmp.tif') + ' ' + \
        os.path.join('tmp','kmz_tmp.tif') + ' -b 1 ' + os.path.join('tmp','kmz_tmp_shp.shp') + ' tracks --config GDAL_CACHEMAX 60000'
subprocess.call(cmd_str,shell=True)
cmd_str='ogr2ogr -f KML ' + outfile + '.kml ' + os.path.join('tmp','kmz_tmp_shp.shp')
subprocess.call(cmd_str,shell=True)

filelist = os.listdir('tmp')
for f in filelist:
    if (f != '.' and f != '..'):
        os.remove(os.path.join('tmp',f))
