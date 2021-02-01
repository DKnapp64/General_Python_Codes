import os
import subprocess
import re
from os.path import join, getsize, basename

f = open('caofs_recovery_zero_list_20161014.txt')
lines = f.read().splitlines()
f.close()

for file in lines:
    result = subprocess.Popen(["fsfileinfo", file], stdout=subprocess.PIPE)
    out = result.stdout.read()
    matchit = re.search(" DISK ", out)
    if (matchit != None):
      print "NOT ON DISK", file
    else:
      print "scp dknapp@ciw6.stanford.edu:"+file+" /Volumes/CAO/Scratch/Recovered/"


