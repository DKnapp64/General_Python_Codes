import os, sys
import numpy as np
import pyproj

ulx4 = np.float64(846250.0)
uly4 = np.float64(2220250.0)
ulx5 = np.float64(218384.5)
uly5 = np.float64(2219085.5)

filelist = ['20180925_203821_gcps.pts', \
            '20180925_204054_gcps.pts', \
            '20180925_204249_gcps.pts', \
            '20180925_204519_gcps.pts', \
            '20180925_204713_gcps.pts', \
            '20180925_204930_gcps.pts', \
            '20180925_205315_gcps.pts', \
            '20180925_205709_gcps.pts', \
            '20180925_205901_gcps.pts', \
            '20180925_210339_gcps.pts', \
            '20180925_210536_gcps.pts', \
            '20180925_210807_gcps.pts', \
            '20180925_211018_gcps.pts']

projutm4 = pyproj.Proj(proj="utm", zone=4, datum='WGS84')
projutm5 = pyproj.Proj(proj="utm", zone=5, datum='WGS84')

for thisfile in filelist:
  with open(thisfile, 'r') as f:
    lines = f.readlines()

  newfile = os.path.splitext(thisfile)[0] + '_new.pts'
  fout = open(newfile, 'w')
  
  fout.write(lines[0])
  fout.write(lines[1])
  fout.write(lines[2])
  fout.write(lines[3])
  fout.write(lines[4])

  for i in (np.arange(len(lines)-5)+5):
    junk = lines[i].split() 
    utmx4 = ((np.float64(junk[0])-0.5)*0.5) + ulx4
    utmy4 = uly4 - ((np.float64(junk[1])-0.5)*0.5)

    lon, lat = projutm4(utmx4, utmy4, inverse=True)
    utmx5, utmy5 = projutm5(lon, lat)
    ptx5 = ((utmx5 - ulx5)/0.5) + 0.5
    pty5 = ((uly5 - utmy5)/0.5) + 0.5

    fout.write(("  %10.2f   %10.2f  %s  %s \n") % (ptx5, pty5, junk[2], junk[3]))

  fout.close()
  print(("Finished %s") % (newfile))

