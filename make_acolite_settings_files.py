#!/usr/bin/env python3
import os, sys
import glob

def main(template, indir, outdir):

  inlist = glob.glob(indir+os.sep+"*/*.SAFE")
  print("Found %d SAFE directories" % (len(inlist)))

  f = open(template, 'r')
  thelines = f.readlines()
  f.close()

  for i in inlist:
    if os.path.isdir(i):
      basefile = os.path.basename(i)
      parts = basefile.split('_')
      datetime = parts[2]
      quadid = parts[5]
      outf = open("acolite_settings_"+datetime+"_"+quadid+".txt", 'w') 
      for j,line in enumerate(thelines[0:-2]):
        outf.write(line)

      outf.write("inputfile="+i+'\n')
      outf.write("output="+outdir+os.sep+quadid+'\n')
      if not os.path.isdir(outdir):
        os.mkdir(outdir+os.sep+quadid)
      outf.close()


if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print("[ ERROR ] you must supply 3 arguments: make_acolite_settings_files.py template indir outdir")
    sys.exit( 1 )

  main( sys.argv[1], sys.argv[2], sys.argv[3] )

