from ftplib import FTP
import os
import re

ftp = FTP('satepsanone.nesdis.noaa.gov')

ftp.login()
ftp.cwd('GIS/GOESwest')
filelist = ftp.nlst()

# initialize name and size lists
tiflist = []
sizelist = []
## find the last [latest] file
for element in filelist:
  if re.search("GoesWest1V[0-3][0-9][0-9][0-2][0-9][0-5][0-9].tif|GoesWest1V_latest.tif", element):
    tiflist.append(element)
    sizelist.append(ftp.size(element))

print(len(tiflist))

## if (sizelist[-1] != sizelist[-2]):
