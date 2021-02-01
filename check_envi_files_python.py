import numpy as np
from osgeo import gdal

inputfile = '/home/dknapp/computing/sites_peru_2013_envi_list.txt'
outputfile = '/home/dknapp/computing/sites_peru_2013_envi_checklist.txt'

with open(inputfile, 'r') as f:
  lines = f.read().splitlines()

f.close()

fout = open(outputfile, 'w')

for idx, imagefile in enumerate(lines):
  ds = gdal.Open(imagefile)
  myarray = np.array(ds.GetRasterBand(1).ReadAsArray())
  minval = myarray.min()
  maxval = myarray.max()
  fout.write(("%s, %f, %f\n") % (imagefile, minval, maxval))
  ds = None
  if ((idx % 500) == 0):
    print(("Finished %d of %d\n") % (idx, len(lines)))


fout.close()
