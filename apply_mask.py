#!/bin/env python2
import numpy as np
import gdal, ogr, osr
import sys

def main(infile, maskfile, outfile):
  ## infile = '/lustre/scratch/cao/nvaughn/prep/dimac_oahu/round3/orthoed/20170930A_EH021554_534_bal_ort_benthos'
  ## maskfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/outtest_mask'
  ## outfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/20170930A_EH021554_534_bal_ort_benthos_masked'
  
  ds = gdal.Open(infile)
  
  ## get data type
  datatype = ds.GetRasterBand(1).DataType
  
  # Create for target raster the same projection as for the value raster
  raster_srs = osr.SpatialReference()
  proj = ds.GetProjection()
  
  outXsize = ds.RasterXSize
  outYsize = ds.RasterYSize
  
  ## create geotransform of mosaic bounds
  gt = ds.GetGeoTransform()
  
  inrgb = ds.ReadAsArray()
  
  mds = gdal.Open(maskfile)
  mask = mds.ReadAsArray()

  masktf = np.equal(mask, 0) 

  inrgb[0,:,:][masktf] = 0
  inrgb[1,:,:][masktf] = 0
  inrgb[2,:,:][masktf] = 0

  driver = ds.GetDriver()
  outDs = driver.Create(outfile, outXsize, outYsize, 3, datatype) 
  outDs.SetGeoTransform(gt)
  outDs.SetProjection(proj)
  outDs.GetRasterBand(1).WriteArray(inrgb[0,:,:].astype(np.uint8))
  outDs.GetRasterBand(2).WriteArray(inrgb[1,:,:].astype(np.uint8))
  outDs.GetRasterBand(3).WriteArray(inrgb[2,:,:].astype(np.uint8))

  del ds, mds, outDs

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print "[ USAGE ] you must supply 3 arguments: mask_inside.py DiMAC_image DiMAC_mask DiMAC_masked"
    print "example : mask_inside.py /lustre/scratch/cao/nvaughn/prep/dimac_oahu/round3/orthoed/20170930A_EH021554_534_bal_ort_benthos outtest_mask 20170930A_EH021554_534_bal_ort_benthos_masked"
    print ""
    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2], sys.argv[3] )
