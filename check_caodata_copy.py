#!/bin/env python3
import sys, os, re
import numpy as np
## import pdb

def main(argv):
  
  ## inlistfile = '/home/dknapp/CAODATA_tape_listings/caodata_tape_listing_0024A.txt'
  ## comparedir = '/Volumes/DGE/CAO/caodata/Raw/Peru12/VSWIR_Raw/20120802'
  ## outputfile = ''
  
  try:
    inlistfile = argv[0]
    comparedir = argv[1]
  except:
    print('Commandname inlistfile comparedir')
    sys.exit(2)
  
  with open(inlistfile, 'r') as f:
    lines = f.read().splitlines()
  
  fullpathtape = []
  fullpathdisk = []
  sizetape = []
  sizedisk = []
  
  for line in lines:
    if re.search('^/', line):
      dirit = line.strip()[0:-1]
    if re.search('^-', line):
      vals = line.split()
      if (len(vals) > 9):
        namepart = ' '.join(vals[8:])
      else:
        namepart = vals[8]
      fileit = dirit + os.sep + namepart
      fileit = fileit.split(os.sep)
      fileit = (os.sep).join(fileit[3:])
      fullpathtape.append(fileit)
      sizetape.append(int(vals[4]))
    
  ## fout = open(outputfile, 'w')
  
  for root, subFolder, files in os.walk(comparedir):
    for item in files:
      tempdisk = (root+os.sep+item).split(os.sep)
      tempdisk = (os.sep).join(tempdisk[6:])
      fullpathdisk.append(tempdisk)
      sizedisk.append(os.stat(root + '/' + item).st_size) 
      
  sizedisk = np.asarray(sizedisk).astype('int64')
  sizetape = np.asarray(sizetape).astype('int64')
  fullpathdisk = np.asarray(fullpathdisk).astype('str')
  fullpathtape = np.asarray(fullpathtape).astype('str')
  
  for k,thisfile in enumerate(fullpathdisk):
    matchit = np.core.defchararray.equal(fullpathtape, thisfile)
    if np.any(matchit):
      ## a match is found, so check the size
      tapesize = sizetape[matchit][0]
      disksize = sizedisk[k]
      if (tapesize == disksize):
        pass
        ## print ("File %s found and sizes match %d" % (thisfile, tapesize))
      else:
        print(("File %s found but sizes do not match %d %d") % (thisfile, tapesize, disksize))
      continue
    else:
      print(("File %s NOT found on tape") % (thisfile))
   
if __name__ == "__main__":
  main(sys.argv[1:])
