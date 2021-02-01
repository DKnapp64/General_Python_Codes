import os, sys
import gdal, osr
import glob
import subprocess

listrb = glob.glob('*_SR_rb.tif')
listrb_sorted = sorted(listrb, reverse=True)

for k,rbfile in enumerate(listrb_sorted):
  try:
    cmd = ['srun', '-n','1','--mem=16000','gdal_translate','-of','GTiff','-b','1','-b','2','-b','3']
    outfile = os.path.splitext(os.path.basename(rbfile))[0] + '_moorea.tif'
    cmd.extend(['-projwin','187200.0','8067600.0','211200.0','8050200.0'])
    cmd.extend(['-a_nodata','-9999.0',rbfile,outfile])
    subprocess.check_call(cmd)
  except Exception as exc:
    sys.stderr.write('Exception raised when subsetting file {}\n'.format(rbfile))
    continue
  print(("Finished with %s: %d of %d") % (rbfile, k, len(listrb_sorted)))


