#!/bin/env python2
import numpy as np
import gdal, ogr, osr
import sys
## import pdb

def main(inptsfile, outscriptfile, outoptfile):
  ## ; ENVI Image to Image GCP File
  ## ; base file: Z:\Scratch\dknapp\Kaneohe\kaneohe_vswir_patch42_dimac_mosaic_match
  ## ; warp file: Z:\Scratch\dknapp\Kaneohe\kaneohe_vswir_flown20170905_rev20170927_patch42_Rb
  ## ; Base Image (x,y), Warp Image (x,y)
  ## ;
  ##        2089.000000       4327.000000        206.000000        434.000000
  ##        4483.000000       2644.000000        445.400000        266.600000
  ##        2834.000000       1642.000000        281.700000        166.300000
  ##        3519.000000       5076.000000        349.000000        508.100000
  ##        4344.000000       2135.000000        432.100000        216.400000
  
  ## inptsfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch25_20170930_atrem_refl_patch25_20171001_dimac_match_sift.pts'
  ## inptsfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch4and5_20171001_atrem_refl_patch4and5_20171001_dimac_match_sift.pts'
  ## outscriptfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch25_gdal_script2.scr'
  ## outfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch4and5_gdal_script2.scr'
  outgcp = 'tempwgcpfile'
  
  with open(inptsfile) as f:
    content = f.readlines()
  
  basefile = content[1][12:].strip()
  warpfile = content[2][12:].strip()
  outwarp = warpfile+'_warped'
  
  baseds = gdal.Open(basefile)
  warpds = gdal.Open(warpfile)
  warpwgcp = warpfile + '.scr'
  
  ## get geotransofrm of image to warp to make sure that it has teh same resolution.
  warpgt = warpds.GetGeoTransform()
  resx = "%6f" % (warpgt[1])
  resy = "%6f" % (warpgt[5])

  gt = baseds.GetGeoTransform()
  bounds = tuple((gt[0], gt[3]+gt[5]*baseds.RasterYSize, gt[0]+gt[1]*baseds.RasterXSize, gt[3]))
  points = np.zeros((len(content)-5, 4))
  content = content[5:]
  gcp_list = []
  
  for j,row in enumerate(content):
    temp = row.split()
    points[j,2] = gt[0] + (float(temp[0]) * gt[1])
    points[j,3] = gt[3] + (float(temp[1]) * gt[5])
    points[j,0] = float(temp[2])
    points[j,1] = float(temp[3])
    z = 0
    gcp = gdal.GCP(points[j,2], points[j,3], z, points[j,0], points[j,1])
    gcp_list.append(gcp)
  
  warpgcpds = None
  baseds = None
  warpds = None
  
  optlun = open(outoptfile, 'wb')
  
  for k in range(points.shape[0]):
    mystring = '-gcp %10.2f %10.2f %10.2f %10.2f' % (points[k,0],points[k,1],points[k,2],points[k,3])
    mystring = ' '.join(mystring.split())
    optlun.write('  '+mystring+' \n')
  
  optlun.close()
  
  outlun = open(outscriptfile, 'wb')
  outlun.write('gdal_translate -of ENVI --optfile '+outoptfile+' \\\n')
  outlun.write('  ' + warpfile + ' ' + outgcp + '\n')
  outlun.write('gdalwarp -of ENVI -r near -tps -tr '+resx+' '+resy+' -t_srs EPSG:32604 ' + outgcp + ' ' + outwarp)
    
  outlun.close()
  
  
if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print "[ USAGE ] you must supply 3 arguments: prepare_gdal_tps.py inptsfile outscriptfile outoptfile"
    print ""
    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2], sys.argv[3] )
