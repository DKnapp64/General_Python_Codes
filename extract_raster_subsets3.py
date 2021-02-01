import os, sys
import gdal, osr
import glob
import subprocess

listsr = glob.glob('*MS_SR.tif')
## listsr = glob.glob('*_SR.tif')
listsr_sorted = sorted(listsr, reverse=True)
## listsr_sorted = listsr_sorted[0:150]

for k,srfile in enumerate(listsr_sorted):
  try:
    cmd = ['gdal_translate','-of','GTiff','-b','1','-b','2','-b','3','-b','4']
    ## cmd = ['gdal_translate','-of','GTiff']
    outfile = os.path.splitext(os.path.basename(srfile))[0] + '_hawaii_sw.tif'
    cmd.extend(['-projwin','187200.0','8067600.0','211200.0','8050200.0'])
    ## cmd.extend(['-a_nodata','0',srfile,outfile])
    cmd.extend(['-a_nodata','0',srfile,outfile])
    subprocess.check_call(cmd)
  except Exception as exc:
    sys.stderr.write('Exception raised when subsetting file {}\n'.format(srfile))
    continue
  print(("Finished with %s: %d of %d") % (srfile, k, len(listsr_sorted)))


