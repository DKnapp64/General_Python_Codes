from ftplib import FTP
import os
import subprocess
import socket
import re
from datetime import timedelta, datetime, tzinfo
import time

def ftp_download():
  ## t = threading.Timer(30.0, ftp_download)
  ## t.daemon = True
  now = datetime.utcnow()
  while (now < datetime(now.year, now.month, now.day, 23, 0, 0)):
    checktime = 0
    while (checktime == 0):
      now = time.gmtime() 
      time.sleep(30.0)
      if (now.tm_min == 37 or now.tm_min == 7):
	print("Minutes are 37 or 7")
        checktime = 1

    print("Past While loop")
    checktime = 0
  ## t.start()
    os.chdir('C:\Users\DKnapp\Desktop\GOES_data')
    try:
      ftp = FTP('satepsanone.nesdis.noaa.gov')
    except (socket.error, socket.gaierror), e:
      print 'ERROR: cannot reach satepsanone.nesdis.noaa.gov'
    print '*** Connected to host satepsanone.nesdis.noaa.gov'
  
    ftp.login()
    ftp.cwd('GIS/GOESeast')
    filelist = ftp.nlst()
  
    tiflist = []
    sizelist = []
  ## find the last and latest file
    for element in filelist:
      if re.search("tif", element):
        tiflist.append(element)
        sizelist.append(ftp.size(element))
  
    if (sizelist[-1] != sizelist[-2]):
      latesttif = tiflist[-3]
    else:
      latesttif = tiflist[-2]
  
    fhandle = open(latesttif, 'wb')
    ftp.retrbinary('RETR '+latesttif, fhandle.write)
    fhandle.close()   # not sure if this is needed
    ftp.quit()
  
    now = time.gmtime()
    mod15time = (now.tm_min // 15) * 15
    if ((mod15time % 30) == 0):
      mod15time = mod15time - 15
  
    nowfile = ('%s%03d%02d%02d%s') % ('GoesEast1V', now.tm_yday, now.tm_hour, mod15time, '.tif')
    print 'NOW file is: %s' % (nowfile)
    ## nowfile = 'GoesEast1V_latest.tif'
    nowsize = ftp.size(nowfile)
    kmlname = (os.path.splitext(nowfile))[0] + "_KML.kmz"
    print 'NOW file is: %s and %d bytes' % (nowfile, nowsize)
    ## see if the file is in the list   
    indexval = filelist.index(nowfile)
    if (nowfile in filelist):
      if ((os.path.isfile(nowfile) == False) and (ftp.size(nowfile) > 2000)):
        fhandle = open(nowfile, 'wb')
        ftp.retrbinary('RETR '+nowfile, fhandle.write)
        fhandle.close()   # not sure if this is needed
    ftp.quit()
    subprocess.call(["gdal_translate", "-of", "KMLSUPEROVERLAY", "-projwin", "-82.0", "2.0", "-75.0", "-6.0", nowfile, kmlname, "-co", "FORMAT=JPEG"]) 

