from ftplib import FTP
import os
import socket
import re
from datetime import timedelta, datetime, tzinfo
import time

def ftp_aircraft():
  ## t = threading.Timer(30.0, ftp_download)
  ## t.daemon = True
  now = datetime.utcnow()
  while (now < datetime(now.year, now.month, now.day, 23, 0, 0)):
    checktime = 0
    while (checktime == 0):
      now = time.gmtime() 
      time.sleep(30.0)
      if (now.tm_min == 39 or now.tm_min == 9):
	print("Minutes are 39 or 9")
        checktime = 1

    print("Past While loop")
    checktime = 0
  ## t.start()
    os.chdir('C:\Users\DKnapp\Desktop\GOES_data')
    try:
      ftp = FTP('dge.stanford.edu')
    except (socket.error, socket.gaierror), e:
      print 'ERROR: cannot reach dge.stanford.edu'
    print '*** Connected to host dge.stanford.edu ***'
  
    ftp.login()
    ftp.cwd('pub/dknapp/GEOS')
    filelist = ftp.nlst()
    kmzlist = []

  ## find the last file
    for element in filelist:
      if element not in kmzlist:
        kmzlist.append(element)
      else:
        print("New KMZ was not created")

    fhandle = open(latesttif, 'wb')
    ftp.retrbinary('RETR '+kmzlist[-1], fhandle.write)
    fhandle.close()   # not sure if this is needed
    ftp.quit()
  
ftp_aircraft()
