import fnmatch
import os

rootDir = '/Volumes/CAO/Sites/Peru'
for dirName, subdirList, fileList in os.walk(rootDir):
  if len(fileList) > 0:
    for filename in fileList:
      if fnmatch.fnmatch(filename, '*dem*') and not(fnmatch.fnmatch(filename, '*dem*.hdr')):
        print os.path.join(dirName, filename)
  
