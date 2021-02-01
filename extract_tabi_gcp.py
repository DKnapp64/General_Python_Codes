import os, sys
import numpy as np

ulx5 = np.float64(218384.5)
uly5 = np.float64(2219085.5)

filelist = ['TABI_2018_09_25_205318_gcp.pts', \
            'TABI_2018_09_25_205712_gcp.pts', \
            'TABI_2018_09_25_205904_gcp.pts', \
            'TABI_2018_09_25_210132_gcp.pts', \
            'TABI_2018_09_25_210342_gcp.pts', \
            'TABI_2018_09_25_210539_gcp.pts', \
            'TABI_2018_09_25_210810_gcp.pts', \
            'TABI_2018_09_25_211021_gcp.pts']

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
    xcoord = ((np.float64(junk[0]) - 0.5) * 0.5) + ulx5
    ycoord = uly5 - ((np.float64(junk[1]) - 0.5) * 0.5)
    fout.write(("  %10.2f   %10.2f  %s  %s \n") % (xcoord, ycoord, junk[2], junk[3]))

  fout.close()
  print(("Finished %s") % (newfile))

