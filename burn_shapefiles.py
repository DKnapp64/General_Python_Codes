import os
import sys
import gdal
import numpy as np
import subprocess
import shutil



prev_filename = sys.argv[1]
cur_dirname = sys.argv[2]
out_filename = sys.argv[3]



if (prev_filename == 'null'):
    #### vvvv this should be some file that contains a reference-size image
    refset = gdal.Open(os.path.join('..','ops','support_dat','tch_keras_wt.tif'),gdal.GA_ReadOnly)
    dat = np.zeros((refset.RasterYSize,refset.RasterXSize))

    driver = gdal.GetDriverByName('ENVI') 
    driver.Register()
    outname = os.path.join('tmp', os.path.basename(out_filename).split('.')[0])
    outDataset = driver.Create(outname,dat.shape[1],dat.shape[0],1,gdal.GDT_Byte)
    outDataset.SetProjection(refset.GetProjection())
    outDataset.SetGeoTransform(refset.GetGeoTransform())
    outDataset.GetRasterBand(1).WriteArray(dat,0,0)
    del outDataset
    subprocess.call('gdal_translate ' + outname + ' ' + out_filename + ' --config GDAL_CACHEMAX 100000 -co COMPRESS=LZW',shell=True)
    os.remove(outname)
    os.remove(outname + '.hdr')
else:
    shutil.copy(prev_filename ,out_filename) 





#### now burn files
filenames = []
for (root, dirs, files) in os.walk(cur_dirname):
  for name in files:
    if (name.split('.')[-1] == 'shp'):
      filenames.append(os.path.join(root,name)) 

for name in filenames:
    cmd_str = 'ogr2ogr -s_srs EPSG:4326 -t_srs EPSG:32610 ' + os.path.join('tmp',os.path.basename(name)) + ' ' + name + ' --config GDAL_CACHEMAX 100000'
    subprocess.call(cmd_str,shell=True)
    cmd_str = 'gdal_rasterize -burn 255 ' + os.path.join('tmp',os.path.basename(name)) + ' ' + out_filename + ' --config GDAL_CACHEMAX 100000'
    subprocess.call(cmd_str,shell=True)

filelist = os.listdir('tmp')
for f in filelist:
    if (f != '.' and f != '..'):
        os.remove(os.path.join('tmp',f))
   

