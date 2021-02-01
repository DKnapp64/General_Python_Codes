import os
import subprocess
import sys




flight_dat_dir='daily_lidar_dat'                 #directory where daily lidar uploads are stored
shape_dat_dir='daily_vswir_dat'                  #directory where daily vswir uploads are stored
cum_lidar_dir='cum_lidar_flights'                #directory of cumulative flight tracks to date, at 30m
cum_vswir_dir='cum_vswir_flights'                #directory of cumulative flight tracks to date, at 30m
cum_comb_dir='cum_comb_flights'                #directory of cumulative flight tracks to date, at 30m

track_output_dir='flight_tracks'                 #directory of flight tracks (binary tif and kmz of coverage)
lbn='cumulative_lidar_and_vswir_data_'           #base of response variable name

if (os.path.isdir(cum_lidar_dir) == False):
    os.mkdir(cum_lidar_dir)
if (os.path.isdir(cum_vswir_dir) == False):
    os.mkdir(cum_vswir_dir)
if (os.path.isdir(track_output_dir) == False):
    os.mkdir(track_output_dir)
if (os.path.isdir('tmp') == False):
    os.mkdir('tmp')
if (os.path.isdir(cum_comb_dir) == False):
    os.mkdir(cum_comb_dir)


dir_to_proc= sys.argv[1]                                 #input directory containing individual response variable images
last_dir_to_proc= sys.argv[2]                            #directory from the previous 'day'

if (last_dir_to_proc == 'null'):
    init=True
else:
    init=False

if (os.path.isdir(os.path.join(flight_dat_dir,dir_to_proc)) == False):
    print 'oops, cant find lidar file: ' + os.path.join(flight_dat_dir,dir_to_proc)
    quit()
if (os.path.isdir(os.path.join(shape_dat_dir,dir_to_proc)) == False):
    print 'oops, cant find lidar file: ' + os.path.join(shape_dat_dir,dir_to_proc)
    quit()


if (init == True):
    cmd_str = 'gdalwarp ' + os.path.join(flight_dat_dir,dir_to_proc,'*') + ' ' + os.path.join(cum_lidar_dir,lbn + dir_to_proc + '.tif') + ' -tr 30 -30 -r med -te 490440.0 9445080.0 1146420.0 10160820.0 -t_srs EPSG:32717 -co COMPRESS=LZW -wo NUM_THREADS=20'
else:
    cmd_str = 'gdalwarp ' + os.path.join(flight_dat_dir,dir_to_proc,'*') + ' ' + os.path.join(cum_lidar_dir,lbn + last_dir_to_proc + '.tif') + ' ' + os.path.join(cum_lidar_dir,lbn + dir_to_proc + '.tif') + ' -tr 30 -30 -r med -co COMPRESS=LZW -wo NUM_THREADS=20'
print cmd_str
subprocess.call(cmd_str,shell=True)


if (init == True):
    cmd_str='python burn_shapefiles.py null ' + dir_to_proc + ' ' + os.path.join(cum_vswir_dir,dir_to_proc + '.tif')
else:
    cmd_str='python burn_shapefiles.py ' + os.path.join(cum_vswir_dir,last_dir_to_proc + '.tif') + ' ' +  os.path.join(shape_dat_dir,dir_to_proc) + ' ' + os.path.join(cum_vswir_dir,dir_to_proc + '.tif')
subprocess.call(cmd_str,shell=True)


if (init == True):
    cmd_str = 'python flight_tracks.py ' + os.path.join(cum_lidar_dir,lbn + dir_to_proc + '.tif') + ' null ' + os.path.join(track_output_dir,lbn + dir_to_proc) + ' ' + os.path.join(cum_comb_dir,lbn + dir_to_proc)
else:
    cmd_str = 'python flight_tracks.py ' + os.path.join(cum_lidar_dir,lbn + dir_to_proc + '.tif') +  ' ' + os.path.join(cum_vswir_dir,dir_to_proc + '.tif') + ' ' + os.path.join(track_output_dir,lbn + dir_to_proc) + ' ' + os.path.join(cum_comb_dir,lbn + dir_to_proc)
subprocess.call(cmd_str,shell=True)

cmd_str='zip ' + os.path.join(track_output_dir,lbn + dir_to_proc + '.kmz') + ' ' + os.path.join(track_output_dir,lbn + dir_to_proc + '.kml')
subprocess.call(cmd_str,shell=True)
os.remove(os.path.join(track_output_dir,lbn + dir_to_proc + '.kml'))


