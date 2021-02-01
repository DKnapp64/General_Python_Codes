import os
import subprocess
import re
import csv
import numpy as np
import random

## with open('/home/dknapp/computing/peru_sites_report_20151230.txt', 'rb') as csvfile:
##   datareader = csv.reader(csvfile, delimiter=',')
##   for row in datareader:
##     print row 

csv = np.genfromtxt('/home/dknapp/computing/testcsv.txt', delimiter=',', dtype=None)

for i in range(0,csv.shape[0]):
  if os.path.isfile(csv[i,0]):
    ## Check to see if it is an ENVI image
    ## If filename ends in ".hdr", skip it
    matchit = re.search(".hdr", csv[i,0])
    if (matchit != None):
      continue 
    else:
      if os.path.isfile(csv[i,0]+".hdr") and (random.random() > 0.5):
        result = subprocess.Popen(["md5sum", csv[i,0]], stdout=subprocess.PIPE)
        out = result.stdout.read()
        print ("%s, %s") % (out.split()[0], out.split()[1])


