import os
import subprocess
import re
from os.path import join, getsize

totaldisk = long(0)
totaltape = long(0)
totalall = long(0)

for root, dirs, files in os.walk('/caofs/Campaigns2/Chilliwack'):
    subtotaldisk = long(0)
    subtotaltape = long(0)
    subtotalall = long(0)
    print root, "consumes",
    print sum(getsize(join(root, name)) for name in files),
    print "bytes in", len(files), "non-directory files"
    for name in files:
      result = subprocess.Popen(["fsfileinfo", join(root, name)], stdout=subprocess.PIPE)
      out = result.stdout.read()
      ## print out
      matchit = re.search(" DISK ", out)
      if (matchit != None):
        totaldisk += getsize(join(root,name))
        subtotaldisk += getsize(join(root,name))
      else:
        totaltape += getsize(join(root,name))
        subtotaltape += getsize(join(root,name))

      totalall += getsize(join(root,name))
      subtotalall += getsize(join(root,name))

    print ("SubTotal Space on Disk: %d") % (subtotaldisk)
    print ("SubTotal Space on Tape: %d") % (subtotaltape)
    print ("SubTotal Space on All: %d") % (subtotalall)
    print  ""

print ("Grand Total Space on Disk: %d") % (totaldisk)
print ("Grand Total Space on Tape: %d") % (totaltape)
print ("Grand Total Space on All: %d") % (totalall)
print  ""
