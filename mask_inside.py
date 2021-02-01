#!/bin/env python2
import numpy as np
import scipy.ndimage as s
import gdal, ogr, osr
import sys

def main(infile, outmaskfile):
  ## infile = '/lustre/scratch/cao/nvaughn/prep/dimac_oahu/round3/orthoed/20170930A_EH021554_534_bal_ort_benthos'
  ## outfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/outtest_mask'
  
  ds = gdal.Open(infile)
  
  ## get data type
  datatype = ds.GetRasterBand(1).DataType
  
  # Create for target raster the same projection as for the value raster
  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt(ds.GetProjectionRef())
  
  outXsize = ds.RasterXSize
  outYsize = ds.RasterYSize
  
  ## outDs = driver.Create(outfile, outXsize, outYsize, 1, datatype) 
  
  ## create geotransform of mosaic bounds
  gt = ds.GetGeoTransform()
  
  ## outDs.SetGeoTransform(gt)
  ## outDs.SetProjection(raster_srs.ExportToWkt())
  
  mask = np.zeros((outYsize, outXsize), dtype=np.bool)
  aband = ds.GetRasterBand(1)
  mask = aband.ReadAsArray()
  mask = np.greater(mask, 0)
  
  for band in range(ds.RasterCount):
    data = ds.GetRasterBand(band+1)
    thisBand = data.ReadAsArray()
    accummask = np.logical_or(np.greater(thisBand, 0), mask)
    mask = accummask
  
  ## outBand = outDs.GetRasterBand(1)
  ## outBand.WriteArray(mask.astype(np.uint8))
  ## outBand.FlushCache()
  
  ## now apply morphological operator to erode around edges
  newmask = s.binary_fill_holes(mask).astype(mask.dtype)
  newmask2 = s.binary_erosion(newmask, iterations=1000).astype(mask.dtype)
  
  driver = ds.GetDriver()
  outDs = driver.Create(outmaskfile, outXsize, outYsize, 1, datatype) 
  
  outBand = outDs.GetRasterBand(1)
  outBand.WriteArray(newmask2.astype(np.uint8))
  outBand.FlushCache()
  
  del ds, outDs

if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print "[ USAGE ] you must supply 2 arguments: mask_inside.py DiMAC_image DiMAC_mask"
    print "example : mask_inside.py /lustre/scratch/cao/nvaughn/prep/dimac_oahu/round3/orthoed/20170930A_EH021554_534_bal_ort_benthos outtest_mask"
    print ""
    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2] )
