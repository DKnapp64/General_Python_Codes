#!/usr/bin/env python3
import PySimpleGUI as sg
import gdal
import os, sys
import numpy as np
import math
from datetime import datetime, timedelta
import ftplib

def extract_from_netcdf(ncfile, layername, ddy, ddx):
  inDS = gdal.Open("NETCDF:{0}:{1}".format(ncfile, layername), gdal.GA_ReadOnly)
  meta = inDS.GetMetadata()
  scale = float(meta[layername+'#scale_factor'])
  nodata = int(meta[layername+'#_FillValue'])
  ## wkt = inDS.GetMetadata('GEOLOCATION')['SRS']
  gt = inDS.GetGeoTransform()
  lin = math.floor((ddy - gt[3])/gt[5])
  pix = math.floor((abs(gt[0]) + ddx)/gt[1])
  thepixel = inDS.GetRasterBand(1).ReadAsArray(pix, lin, 1, 1)
  inDS = None
  if (thepixel[0,0] != nodata):
    return (thepixel[0,0] * scale)
  else:
    return None

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

sg.change_look_and_feel('Dark Blue 3')  # please make your creations colorful

layout = [	[sg.T('Output File:'), sg.In('', background_color='white', size=(35,1), key='input'), sg.SaveAs(target='input')], 
          	[sg.T('Type of Data:'), sg.Combo(['SST','SST Anomaly'])], 
          	[sg.T('Start Date:'), sg.In('', background_color='white', size=(10,1), key='stdate'), sg.CalendarButton('Start Date', target='stdate')], 
          	[sg.T('End Date:'), sg.In('', background_color='white', size=(10,1), key='eddate'), sg.CalendarButton('End Date', target='eddate')], 
          	[sg.T('Latitude:'), sg.In('', background_color='white', size=(12,1), key='lat'), sg.T('Longitude:'), sg.In('', background_color='white', size=(12,1), key='lon')], 
  		[sg.OK(), sg.Cancel()]] 

window = sg.Window('Extract SST or SST Anomaly', layout)

event, values = window.Read()

if (event == 'OK'):
  try:
    stdate = values['stdate'][0:10]
  except KeyError:
    pdb.set_trace()
    window.close() 
  try:
    eddate = values['eddate'][0:10]
  except KeyError:
    pdb.set_trace()
    window.close() 
  try:
    if (values[0] == 'SST'):
      datachoice = 'sst'
    elif (values[0] == 'SST Anomaly'):
      datachoice = 'ssta'
    else:
      window.close()
  except IndexError:
    pdb.set_trace()
    window.close() 
  try:
    outfile = values['input']
  except KeyError:
    pdb.set_trace()
    window.close() 
  try:
    mylat = float(values['lat'])
  except KeyError:
    pdb.set_trace()
    window.close() 
  except ValueError:
    pdb.set_trace()
  try:
    mylon = float(values['lon'])
  except KeyError:
    pdb.set_trace()
    window.close() 
  except ValueError:
    pdb.set_trace()
  print("%10s %10s %s %12.8f %12.8f %s" % (stdate, eddate, datachoice, mylat, mylon, outfile)) 

  ## get_temperatures(stdate, eddate, mylat, mylon, datachoice, outfile)
if (event == 'Cancel'):
  window.close()

server = 'ftp.star.nesdis.noaa.gov'

if (datachoice == 'sst'):
  thedir = '/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/sst/'
  layername = "analysed_sst"
else:
  thedir = '/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/ssta/'
  layername = "sea_surface_temperature_anomaly"

st = datetime(int(stdate[0:4]), int(stdate[5:7]), int(stdate[8:10]))
ed = datetime(int(eddate[0:4]), int(eddate[5:7]), int(eddate[8:10]))
myst = stdate[0:4] + stdate[5:7] + stdate[8:10]
myed = eddate[0:4] + eddate[5:7] + eddate[8:10]
styear = stdate[0:4]
edyear = eddate[0:4]

thefiles = []

ftp = ftplib.FTP(server)
ftp.login('anonymous', 'anonymous') 
ftp.cwd(thedir)

for yr in range(int(styear), int(edyear)+1):
  ftp.cwd(thedir+('%04d' % yr))
  filelist = ftp.nlst('*.nc')
  thefiles.extend(filelist)

thefiles = np.asarray(sorted(thefiles))
thedates = np.asarray([ os.path.splitext(k)[0][-8:] for k in thefiles ])
within = np.logical_and(np.char.greater_equal(thedates, myst), np.char.less_equal(thedates, myed))
thefiles = thefiles[within]

f = open(outfile, 'w')

for j,i in enumerate(thefiles):
  thisyr = os.path.splitext(i)[0][-8:-4]
  datestr = thisyr + '-' + os.path.splitext(i)[0][-4:-2] + '-' + os.path.splitext(i)[0][-2:]
  try:
    ftp.cwd(thedir+thisyr)
    ## ftp.retrbinary("RETR " + i, open('./'+i, "wb").write) 
    localfile = open(i, 'wb') 
    ftp.retrbinary("RETR " + i, localfile.write, 1024) 
    localfile.close()
    ## print("Downloaded: %s" + i)
    value = extract_from_netcdf(i, layername, float(mylat), float(mylon))
    f.write('%10s, %12.8f, %12.8f, %s, %8f\n' % (datestr, float(mylat), float(mylon), layername, value))
    os.remove(i)
    sg.OneLineProgressMeter('Progress', j+1, len(thefiles), 'progress', 'File %d of %d' % (j+1, len(thefiles)))
  except:
    print("Error: File could not be downloaded " + file)

ftp.quit()
f.close()

