import gdal, osr
import os, sys
import numpy as np
import glob
from datetime import datetime, timedelta

theyears = ['2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009',
'2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']

thefiles = []

for thisyear in theyears:
  thefiles.extend(glob.glob(thisyear+os.sep+"*.nc"))

thefiles = sorted(thefiles)

indatafile = 'restoration_coral.txt'
## Location        Latitude_DMS    Longitude_DMS   Genus   Transplant_date Length_monitored_months Survival Rate (%)
## Palau - Ioul Lukes Reef "7▒ 17' 14.28"" N"      "134▒ 30' 12.24"" E"    Acropora        "September 26, 2007"   18       80
indata = np.genfromtxt(indatafile, dtype=[('sitename', 'S43'), ('lat', 'S20'), ('lon', 'S20'), ('genus', 'S20'), ('transdate', 'S20'),
 ('length', 'i8'), ('survrate', 'i8')], skipheader=1, delimiter='\t', autostrip=True)

layername = "analysed_sst"

outfile = "sst_output.txt"
f = open(outfile, 'w')

for k,rec in enumerate(indata):
  tempy = rec['lat'].decode().strip()[1:-1].split()
  tempx = rec['lon'].decode().strip()[1:-1].split()
  if (tempy[-1] == 'N'):
    ysign = 1
  else:
    ysign = -1
  if (tempx[-1] == 'E'):
    xsign = 1
  else:
    xsign = -1
  ddx = xsign * (tempx[0] + float(tempx[1])/60.0 + float(tempx[2])/3600.0)
  ddy = ysign * (tempy[0] + float(tempy[1])/60.0 + float(tempy[2])/3600.0)
  genus = rec['genus'].decode()
  txtdate = rec['transdate'].decode()[1:-1]
  dateobj = datetime.strptime(txtdate, '%B %d, %Y')
  stsearch = ("%04d" % (dateobj.year-1)) + ("%02d" % dateobj.month) + ("%02d" % dateobj.day)
  endsearch = ("%04d" % (dateobj.year)) + ("%02d" % dateobj.month) + ("%02d" % dateobj.day)
  stindex = np.flatnonzero(np.core.defchararray.find(thefiles, stsearch[0:4]+os.sep+stsearch) != -1)
  endindex = np.flatnonzero(np.core.defchararray.find(thefiles, endsearch[0:4]+os.sep+endsearch) != -1)
  stind = stindex[0]
  endind = endindex[0] - 1
  beforeset = thefiles[stind:endind] 

  listdata = []

  for j,thisfile in enumerate(beforeset):
    inDS = gdal.Open("NETCDF:{0}:{1}".format(thisfile, layername), gdal.GA_ReadOnly)
    meta = inDS.GetMetadata()
    offset = float(meta['analysed_sst#add_offset'])
    scale = float(meta['analysed_sst#scale_factor'])
    nodata = int(meta['analysed_sst#_FillValue'])
    wkt = inDS.GetMetadata('GEOLOCATION')['SRS']
    gt = inDS.GetGeoTransform()
    lin = math.floor((gt[3] - ddy)/gt[5])
    pix = math.floor((abs(gt[0]) + ddx)/gt[1])
    thepixel = inDS.GetRasterBand(1).ReadAsArray(pix, lin, 1, 1)
    if (thepixel != nodata):
      listdata.append(offset + thepixel * scale)
    inDS = None

  ## got all the data for that point, now get stats
  arrdata = np.asarray(listdata)
  beforenumvals = len(listdata)
  beforemean = np.mean(arrdata) - 273.15
  beforestd = np.std(arrdata) - 273.15
  beforemin = np.min(arrdata) - 273.15
  beforemax = np.max(arrdata) - 273.15
    
  lentime = rec['length']
  if (lentime >= 12):
    lendelta = datetime.timedelta(years=(lentime//12)) + datetime.timedelta(days=(lentime%12)*30)
  else:
    lendelta = datetime.timedelta(days=lentime*30)
  endmon = dateobj + lendelta
  stsearch = ("%04d" % (dateobj.year)) + ("%02d" % dateobj.month) + ("%02d" % dateobj.day)
  endsearch = ("%04d" % (endmon.year)) + ("%02d" % endmon.month) + ("%02d" % endmon.day)
  stindex = np.flatnonzero(np.core.defchararray.find(thefiles, stsearch[0:4]+os.sep+stsearch) != -1)
  endindex = np.flatnonzero(np.core.defchararray.find(thefiles, endsearch[0:4]+os.sep+endsearch) != -1)
  stind = stindex[0]
  endind = endindex[0]
  afterset = thefiles[stind:endind] 

  listdata = []

  for j,thisfile in enumerate(afterset):
    inDS = gdal.Open("NETCDF:{0}:{1}".format(thisfile, layername), gdal.GA_ReadOnly)
    meta = inDS.GetMetadata()
    offset = float(meta['analysed_sst#add_offset'])
    scale = float(meta['analysed_sst#scale_factor'])
    nodata = int(meta['analysed_sst#_FillValue'])
    wkt = inDS.GetMetadata('GEOLOCATION')['SRS']
    gt = inDS.GetGeoTransform()
    lin = math.floor((gt[3] - ddy)/gt[5])
    pix = math.floor((abs(gt[0]) + ddx)/gt[1])
    thepixel = inDS.GetRasterBand(1).ReadAsArray(pix, lin, 1, 1)
    if (thepixel[0,0] != nodata):
      listdata.append(offset + thepixel * scale)
    inDS = None

  ## got all the data for that point, now get stats
  arrdata = np.asarray(listdata)
  afternumvals = len(listdata)
  aftermean = np.mean(arrdata) - 273.15
  afterstd = np.std(arrdata) - 273.15
  aftermin = np.min(arrdata) - 273.15
  aftermax = np.max(arrdata) - 273.15
    
  f.write("%s;%s;%14.8f;%14.8f;%s;%8.2f;%8.2f;%8.2f;%8.2f;%6d;%8.2f;%8.2f;%8.2f;%8.2f;%6d\n" %
     (rec['site_name'], txtdate, ddy, ddx, genus, beforemean, beforesd, beforemin, beforemax, beforenumvals,
     aftermean, aftersd, aftermin, aftermax, afternumvals)) 
  f.flush()
  print("Finished %d of %d" % (k, len(indata)))
  
f.close()
