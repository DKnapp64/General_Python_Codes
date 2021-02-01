import xml.etree.ElementTree as ET  
from datetime import datetime

xmlfile = "XMLS/20180124_211151_0f2e_3B_AnalyticMS_metadata.xml"
tree = ET.parse(xmlfile)  
root = tree.getroot()

# get Center coordinate
pntstring = root[3][0][1][0][0].text
## '-155.84954099 20.0185364346'
(loncoord, latcoord) = np.double(pntstring.split())

# get Acquisition Time
acqtimestr = root[2][0][3][0][6].text
acqtype = root[2][0][3][0][6].text
## '2018-01-24T21:11:51+00:00'

## get orbit direction
orbitDir = root[2][0][3][0][0].text

## get solar Azimuth
solarAz = np.double(root[2][0][3][0][2].text)

## get solar Elevation
solarElev = np.double(root[2][0][3][0][3].text)

## get apcecraft View angle
spacecraftView = np.double(root[2][0][3][0][5].text)

