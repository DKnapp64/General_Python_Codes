import urllib2
import os
import subprocess
import socket
import re
from datetime import timedelta, datetime, tzinfo
import time
from subprocess import Popen, PIPE

############ User Specified Parameters - configure to your system/prefs ##################
##########################################################################################
# Specify the google drive root folder for 'California_Clouds' or wherever you want to write to
root_folder_id = '0ByYTB5k_a6rsbVZ1UzQzSG1iNzA'

cloud_out_dir = 'cloud_output/'
root_cloud_dir = '/home/dknapp/cloud_map/' + cloud_out_dir
temp_dir = '/home/dknapp/cloud_map/Himawari8_data/'
## projection info for Himawari-8 Full disk imagery
##
## geostationary:proj4 = "+proj=geos +lon_0=140.7 +h=35785863 +x_0=0 +y_0=0 +a=6378137 +b=6356752.3 +units=m +no_defs "
## geostationary:proj_name = "GEOS141"
## geostationary:grid_mapping_name = "geostationary"
## geostationary:longitude_of_projection_origin = 140.7
## geostationary:perspective_point_height = 35785863.
## geostationary:satellite_height = 35785863.
## geostationary:semi_major_axis = 6378137.
## geostationary:semi_minor_axis = 6356752.3
## geostationary:sweep_angle_axis = "y"
## geostationary:GeoTransform = -5500000., 500., 0., 5500000., 0., -500.
## geostationary:spatial_ref = 'PROJCS["unnamed",GEOGCS["unnamed ellipse",DATUM["unknown",SPHEROID["unnamed",6378137,298.2570248822722]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Geostationary_Satellite"],PARAMETER["central_meridian",140.7],PARAMETER["satellite_height",35785863],PARAMETER["false_easting",0],PARAMETER["false_northing",0]]'

## UL 110.0 10.0           
## UL -3114096.39     1066589.22
## LL 110.0 0.0
## LL -3168665.06     0.00
## LR 120.0 0.0
## LR -2226001.56     0.00
## UR 120.0 10.0
## UR -2187064.68     1082616.11
##########################################################################################

# check a path name on google drive
def check_path(path_name):
    p1 = Popen(['drive','list','-t',path_name,'-n'],stdout=PIPE,stderr=PIPE)
    p2 = Popen(['cut','-d',' ','-f','1'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
    stdout,stderr = p2.communicate()
    line_by_line = stdout.split('\n') 
    if (len(line_by_line) == 0):
        return 0
    else:
        for n in range(0,len(line_by_line)):
            p1 = Popen(['drive','info','--id',line_by_line[n]],stdout=PIPE,stderr=PIPE)
            p2 = Popen(['grep','Parents'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
            p3 = Popen(['cut','-d',' ','-f','2'],stdin=p2.stdout,stdout=PIPE,stderr=PIPE)
            stdout, stderr = p3.communicate()
            if (stdout.strip(' \t\n\r') == root_folder_id):
                # then get folder id
                p1 = Popen(['drive','info','--id',line_by_line[n]],stdout=PIPE,stderr=PIPE)
                p2 = Popen(['grep','Id','--id'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
                p3 = Popen(['cut','-d',' ','-f','2'],stdin=p2.stdout,stdout=PIPE,stderr=PIPE)
                stdout, stderr = p3.communicate()

                return line_by_line[n]

    # if we make it through and never found the correct parent folder, delete and return
    return 0


# make a directory on google drive
def make_path(path_name):
    print 'Making new folder ' + path_name + '...'

    # make the folder, and get it's parent ID
    p1 = Popen(['drive', 'folder','-t',path_name,'-p',root_folder_id, '--share'], stdout=PIPE, stderr=PIPE)
    p2 = Popen(['grep','Id'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
    p3 = Popen(['cut','-d',' ','-f','2'],stdin=p2.stdout,stdout=PIPE,stderr=PIPE)
    stdout, stderr = p3.communicate()
    new_folder_id = stdout.strip(' \t\n\r')

    # print out the new folder's id
    print "New folder ID: " + new_folder_id
    print stderr

    return new_folder_id

# check to see if a file exists in the given parent folder, on google drive
def check_file(file_name, parent_folder_id):
    p1 = Popen(['drive','list','-t',file_name,'-n'],stdout=PIPE,stderr=PIPE)
    p2 = Popen(['cut','-d',' ','-f','1'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
    stdout,stderr = p2.communicate()
    line_by_line = stdout.split('\n') 
    if (len(line_by_line) == 0):
        return False
    else:
        for n in range(0,len(line_by_line)):
            p1 = Popen(['drive','info','--id',line_by_line[n]],stdout=PIPE,stderr=PIPE)
            p2 = Popen(['grep','Parents'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
            p3 = Popen(['cut','-d',' ','-f','2'],stdin=p2.stdout,stdout=PIPE,stderr=PIPE)
            stdout, stderr = p3.communicate()
            if (stdout.strip(' \t\n\r') == parent_folder_id):
                # then get folder id
                p1 = Popen(['drive','info','--id',line_by_line[n]],stdout=PIPE,stderr=PIPE)
                p2 = Popen(['grep','Id','--id'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
                p3 = Popen(['cut','-d',' ','-f','2'],stdin=p2.stdout,stdout=PIPE,stderr=PIPE)
                stdout, stderr = p3.communicate()

                return True

    # if we make it through and never found the correct parent folder, delete and return
    return False


# delete a directory on google drive
def delete_path(path_name):
    print 'Deleting yesterday folder ' + path_name + '...'

    p1 = Popen(['drive','list','-t',path_name, '-n'],stdout=PIPE,stderr=PIPE)
    p2 = Popen(['cut','-d',' ','-f','1'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
    stdout,stderr = p2.communicate()
    line_by_line = stdout.split('\n') 
    if (len(line_by_line) == 0):
        return False
    else:
        for n in range(0,len(line_by_line)):
            p1 = Popen(['drive','delete','--id',line_by_line[n]],stdout=PIPE,stderr=PIPE)
            ## p2 = Popen(['grep','Parents'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
            ## p3 = Popen(['cut','-d',' ','-f','2'],stdin=p2.stdout,stdout=PIPE,stderr=PIPE)
            ## stdout, stderr = p3.communicate()
            ## if (stdout.strip(' \t\n\r') == parent_folder_id):
                # then get folder id
            ##    p1 = Popen(['drive','info','--id',line_by_line[n]],stdout=PIPE,stderr=PIPE)
            ##    p2 = Popen(['grep','Id','--id'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
            ##    p3 = Popen(['cut','-d',' ','-f','2'],stdin=p2.stdout,stdout=PIPE,stderr=PIPE)
            ##    stdout, stderr = p3.communicate()
            return True

# upload a file to the given directory on google drive
def upload_file(file_name, parent_file_id):

    # First, make sure the file's not already there
    file_exists = check_file(file_name,parent_file_id)
    if (file_exists == True):
        print 'File exists, sleeping...'
    
    else:
        print 'Attempting to upload...'

        # make the folder, and get it's parent ID
        p1 = Popen(['drive', 'upload','-f',file_name,'-p',parent_file_id, '--share'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = p1.communicate()

        # print out the new folder's id
        print stdout
        print stderr
  

os.chdir(temp_dir)
# begin loop
while True:
  # get current time
  nowtime = datetime.utcnow() 

  ## CREATE DATE STRING FROM LATEST TIME
  nowtime_sabah = nowtime + timedelta(hours=8)
  datestring = "%04d%02d%02d" % (nowtime_sabah.year, nowtime_sabah.month, nowtime_sabah.day)
  yesterday_sabah = nowtime_sabah - timedelta(days=1)
  yesterstring = "%04d%02d%02d" % (yesterday_sabah.year, yesterday_sabah.month, yesterday_sabah.day)

  # test to see if day directory exists locally
  if not(os.path.isdir(root_cloud_dir + datestring)):
    os.makedirs(root_cloud_dir + datestring) 

  # check path on google drive
  current_path_id = check_path(datestring)
  if (current_path_id == 0):
    current_path_id = make_path(datestring)        

  # check path on google drive for yesterday directory
  # if yesterday directory exists, delete it
  yesterday_path_id = check_path(yesterstring)
  if (yesterday_path_id != 0):
    success = delete_path(yesterstring)

  ## set current directory to the latest date string
  currentdir = root_cloud_dir + datestring + '/' 

  projstring = '"'+'+proj=geos +lon_0=140.7 +h=35785863 +x_0=0 +y_0=0 +a=6378137 +b=6356752.3 +units=m +no_defs'+'"'

  # only process during daylight hours in Sabah - check on 15 minute intervals
  nowtime = datetime.utcnow() - timedelta(seconds=1200)
  minuteround = (nowtime.minute / 10) * 10
  print('UTC is: %02d %02d %02d' % (nowtime.hour, nowtime.minute, nowtime.second))
  print('Sabah time is: %02d %02d %02d' % (nowtime_sabah.hour, nowtime_sabah.minute, nowtime_sabah.second))
  kmlstartfile = currentdir + 'sabah_clouds_'+('%02d%02d' % (nowtime.hour, minuteround))\
    +'_KML.kmz'

  while (True):
    do10sleep = True
    # get current time
    nowtime = datetime.utcnow() 
    nowtime_sabah = nowtime + timedelta(hours=8)

    if ((nowtime_sabah.hour > 4) and (nowtime_sabah.hour < 17)):
      datestring = "%04d%02d%02d" % (nowtime_sabah.year, nowtime_sabah.month, nowtime_sabah.day)
      yesterday_sabah = nowtime_sabah - timedelta(days=1)
      yesterstring = "%04d%02d%02d" % (yesterday_sabah.year, yesterday_sabah.month, yesterday_sabah.day)
      print(("Current date string and yesterstring for Sabah: %s %s") % (datestring, yesterstring))

      minuteround = (nowtime.minute / 10) * 10

      kmlname = currentdir + 'sabah_clouds_'+('%02d%02d' % (nowtime.hour, minuteround))\
        +'_KML.kmz'
      kmlname_for_upload =  temp_dir+os.path.basename(kmlname)

      # check path on google drive for yesterday directory
      # if yesterday directory exsists, delete it
      yesterday_path_id = check_path(yesterstring)
      if (yesterday_path_id != 0):
        print (("Deleting yesterstring: %s") % (yesterstring))
        success = delete_path(yesterstring)        

      # check path on google drive
      current_path_id = check_path(datestring)
      if (current_path_id == 0):
        current_path_id = make_path(datestring)

      # get file from URL
      try:
        # url = 'http://www.data.jma.go.jp/mscweb/data/himawari/img/se3/se3_b13_'\
        #         +("%02d%02d" % (nowtime.hour, minuteround))+'.jpg'
        url = 'http://rammb.cira.colostate.edu/ramsdis/online/images/latest_hi_res/himawari-8/full_disk_ahi_true_color.jpg'
        print(url)
        filename = os.path.basename(url)
        print(filename)
        site = urllib2.urlopen(url)
        datelist = site.info().getdate('last-modified')
        print(datelist)

        if (datelist[2] == datetime.utcnow().day):
          newfilename = os.path.basename(url)
          f = open(temp_dir+filename, "wb")
          f.write(site.read()) 
          site.close()
          f.close()

          subprocess.call("gdal_translate -of VRT -a_srs " + projstring + " -gcp 2750 2750 0.0 0.0 "\
            +"-gcp 1192.95 2216.71 -3114096.39 1066589.22 -gcp 1165.67 2750 -3168665.06 0.0 -gcp 1637.00 2750 -2226001.56"\
            +" 0.0 -gcp 1656.47 2208.69 -2187064.68 1082616.11 " + temp_dir+filename + " "+temp_dir+"temp_vrt.vrt", shell=True)
          subprocess.call("gdalwarp -s_srs " + projstring + " -t_srs EPSG:4326 -te 110.0 0.0 120.0 10.0 "+temp_dir\
            +"temp_vrt.vrt " +temp_dir+"temp_gtif.tif", shell=True)
          subprocess.call("gdal_translate -of KMLSUPEROVERLAY -projwin 114.0 10.0 120.0 3.0 "+\
            temp_dir+"temp_gtif.tif "+kmlname_for_upload+" -co FORMAT=JPEG", \
            shell=True) 
          os.remove(temp_dir+"temp_vrt.vrt")
          os.remove(temp_dir+"temp_gtif.tif")
          ## subprocess.call("rm "+temp_dir+"temp_vrt.vrt "+temp_dir+"temp_gtif.tif")

          # now put it on the drive
          upload_file(kmlname_for_upload, current_path_id)

        else:
          print 'New file not ready yet, checking back soon'

      except:
        print 'ERROR: problem reaching http://rammb.cira.colostate.edu/ramsdis/online/images/latest_hi_res/himawari-8/full_disk_ahi_true_color.jpg'

    else:
      print ('Waiting for daylight: sleeping for 15 minutes') 
      ## IF IT IS NOT DURING QUASI-DAYLIGHT HOURS, SLEEP FOR 15 MINUTES
      time.sleep(15*60)
      do10sleep = False

    # sleep for 10 minutes in between normal checks
    if do10sleep:
      print ('Doing regular 10 minute wait during Sabah daylight hours.') 
      time.sleep(10*60.0)
  
