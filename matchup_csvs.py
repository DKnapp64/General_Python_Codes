import numpy as np
import os, sys

asdcsvfile = "Moorea_Dove_BGR_from_ASD.csv"
dovecsvfile = "20190604_moorea_tile_sr_rb.csv"
outfile = "Moorea_Dove_ASD_matched.csv"

asddata = np.genfromtxt(asdcsvfile, dtype=[('fname', 'S40'), ('blue', 'f8'), ('green', 'f8'), ('red', 'f8')], delimiter=',')
dovedata = np.genfromtxt(dovecsvfile, dtype=[('fname', 'S20'), ('imagename', 'S20'), ('blue', 'f8'), ('green', 'f8'), ('red', 'f8')], 
  delimiter=',', skip_header=1, autostrip=True)

f = open(outfile, 'w')

for rec in asddata:
  theasdname = rec['fname'][0:9]
  for drec in dovedata:
    if (drec['fname'] == theasdname):
      bigstring = ("%s, " % (theasdname))
      bigstring += ("%8.4f, %8.4f, %8.4f, %8.4f, %8.4f, %8.4f\n") % (rec['blue'], rec['green'], rec['red'], drec['blue'], drec['green'], drec['red'])
      f.write(bigstring)

f.close()

