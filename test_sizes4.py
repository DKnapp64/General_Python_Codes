import os
import subprocess
import re
import csv
from os.path import join, getsize, basename

f = open('final_matched_nick_20161014.csv', 'rb')
reader = csv.reader(f)
mylist = list(reader)

f.close()

filelist = [ row[0] for row in mylist ]

filelist = filelist[1:]

for file in filelist:
    result = subprocess.Popen(["fsfileinfo", file], stdout=subprocess.PIPE)
    out = result.stdout.read()
    matchit = re.search(" DISK ", out)
    if (matchit != None):
      print "NOT ON DISK", file
    else:
      print "scp dknapp@ciw6.stanford.edu:"+file+" /Volumes/CAO/Scratch/Recovered/"



