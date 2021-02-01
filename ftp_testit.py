from ftplib import FTP
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
#root_folder_id = '0BxWoadSr2PBhfnhjVTBwNXYxN3VLdkxVRk5CWFVxcmpUNjZSS3ZBZmRtd2NTTXQteUJxRzg'
root_folder_id = '0ByYTB5k_a6rsbVZ1UzQzSG1iNzA'
##root_folder_id = '0ByYTB5k_a6rsfmszcGVNd1AxSVpWWmZMRFRUa1hBMWlWQUtXR0JUZUstYUtTaWZtcWRqYjA'
#root_folder_id = '0ByYTB5k_a6rsNnNqbjMtUnRQVXM'


cloud_out_dir = 'cloud_output/'
root_cloud_dir = '/home/dknapp/cloud_map/' + cloud_out_dir
temp_dir = '/home/dknapp/cloud_map/GOES_data/'


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
    p1 = Popen(['drive', 'folder','-t',path_name,'-p',root_folder_id], stdout=PIPE, stderr=PIPE)
    p2 = Popen(['grep','Id'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE)
    p3 = Popen(['cut','-d',' ','-f','2'],stdin=p2.stdout,stdout=PIPE,stderr=PIPE)
    stdout, stderr = p3.communicate()
    new_folder_id = stdout.strip(' \t\n\r')

    # print out the new folder's id
    print "New folder ID: " + new_folder_id
    print stderr

    return new_folder_id

# check to see if a file exists in the given parent folder, on google drive
def check_file(file_name,parent_folder_id):
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



# upload a file to the given directory on google drive
def upload_file(file_name,parent_file_id):

    # First, make sure the file's not already there
    file_exists = check_file(file_name,parent_file_id)
    if (file_exists == True):
        print 'File exists, sleeping...'
    
    else:
        print 'Attempting to upload...'

        # make the folder, and get it's parent ID
        p1 = Popen(['drive', 'upload','-f',file_name,'-p',parent_file_id], stdout=PIPE, stderr=PIPE)
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
  datestring = "%04d%02d%02d" % (nowtime.year, nowtime.month, nowtime.day)

  # test to see if day directory exists locally
  if not(os.path.isdir(root_cloud_dir + datestring)):
    os.makedirs(root_cloud_dir + datestring) 

  # check path on google drive
  current_path_id = check_path(datestring)
  if (current_path_id == 0):
    current_path_id = make_path(datestring)        

  ## set current directory to the latest date string
  currentdir = root_cloud_dir + datestring + '/' 

  # only process during daylight hours in Hawaii - check on 15 minute intervals
  if ((datetime.now().hour > 6) and (datetime.now().hour < 17)):
    print('Now is: %02d %02d %02d' % (nowtime.hour, nowtime.minute, nowtime.second))
    checktime = 0
    while (checktime == 0):

      # establish ftp connection
      try:
        ftp = FTP('satepsanone.nesdis.noaa.gov')

        ftp.login()
        ftp.cwd('GIS/GOESwest')
        filelist = ftp.nlst()
    
        # initialize name and size lists
        tiflist = []
        sizelist = []
        ## find the last [latest] file
        for element in filelist:
          if re.search("GoesWest1V[0-3][0-9][0-9][0-2][0-9][0-5][0-9].tif", element):
            tiflist.append(element)
            sizelist.append(ftp.size(element))
    
        ## identify latest TIF file
        latesttif = tiflist[-1]
  
        file_name_to_check = (os.path.splitext(latesttif))[0] + '_KML.kmz'
        file_exists = check_file(file_name_to_check,current_path_id)
  
        # check if we have the file  -if we do, download it and then upload it
        if (file_exists == False):
          checktime = 1
          
          # download
          print 'Latest TIF is: %s' % (latesttif)
          fhandle = open(latesttif, 'wb')
          ftp.retrbinary('RETR '+latesttif, fhandle.write)
          fhandle.close()   # not sure if this is needed
          ftp.quit()
  
  
          # upload
          nowfile = latesttif
          print 'NOW file is: %s' % (nowfile)
          kmlname = '"'+currentdir + (os.path.splitext(nowfile))[0] + "_KML.kmz"+'"'
          kmlname_for_upload =  '../' + cloud_out_dir + datestring +'/' +  (os.path.splitext(nowfile))[0] + '_KML.kmz'
          print 'NOW KML file is: %s' % (kmlname)
          subprocess.call("gdal_translate -of KMLSUPEROVERLAY -projwin -157.0 21.5 -154.0 18.0 "+\
                          nowfile + " " + kmlname + " -co FORMAT=JPEG", shell=True) 
          print "gdal_translate -of KMLSUPEROVERLAY -projwin -157.0 21.5 -154.0 18.0 "+ \
                 nowfile + " " + kmlname + " -co FORMAT=JPEG"
  
          # now put it on the drive
          upload_file(kmlname_for_upload,current_path_id)
  
        else:
          print 'file exists, checking back soon'

      except (socket.error, socket.gaierror), e:
        print 'ERROR: cannot reach satepsanone.nesdis.noaa.gov...will try again in 5 min'

      # sleep for 5 minutes in between checks
      time.sleep(5*60.0)


  else:
    print ('Waiting for daylight: sleeping for 15 minutes') 
    ## IF IT IS NOT DURING QUASI-DAYLIGHT HOURS, SLEEP FOR 15 MINUTES
    time.sleep(15*60)









