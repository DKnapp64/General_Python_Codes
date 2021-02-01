#!/usr/bin/python2
import os, sys
# Windows and linux slashes go in opposite directions.
# Uncomment the slash appropriate for your system.
systemslash='/'
# systemslash='\'

def get_list_of_files(inDirectory, container=[]):
    for entry in os.listdir(inDirectory):
        entry = inDirectory+systemslash+entry
        if os.path.isdir(entry):
            get_list_of_files(entry,container)
        filesize = os.path.getsize(entry)
        fileandsize = (filesize, entry)
        container.append(fileandsize)
    return container

def main(indir):
    Final_List_of_Files = get_list_of_files(indir)
    Final_List_of_Files.sort(reverse=True)

    for record in Final_List_of_Files:
       print str(record).strip("()")

if __name__ == "__main__":

  if len( sys.argv ) != 2:
      print "[ ERROR ] you must supply a directory name under which files will be listed by size (largest first)."
      print "example: ./find_large_sort.py /Volumes/Data/Shared/Labs/Asner/Private/Research/Researcher/Knapp"
      sys.exit( 1 )

  main(sys.argv[1])


