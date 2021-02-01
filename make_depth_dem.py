#!/bin/env python2
import numpy as np
import gdal, ogr, osr
import pyproj
import sys, os
## import pdb

def main(indepthfile, indemfile, outfile):
  ## indepthfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/MERCs/papabay_merc_20170929_mosaic_dep'
  ## indepthfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/MERCs/honaunau_merc_20170929_mosaic_dep'
  ## indemfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/MERCs/coral_milolii_papa_merc_surface_0p4'
  ## indemfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/MERCs/coral_honaunau_merc_surface_0p65'
  ## outfile = 'coral_honaunau_merc_20170929_coral_surface'
  ## egmfile = '/Volumes/DGE/CAO/caodata/support/AIG_Support_Data/egm96'
  
  egmfile = '/Volumes/DGE/CAO/caodata/support/AIG_Support_Data/egm2008-2_5_float32'
  listdatasets = []
  
  egmds = gdal.Open(egmfile)
  ## (0.0, 0.25, 0.0, 90.0, 0.0, -0.25)
  
  ## egm file is a bit weird, since it is global
  ## the upper left corner is at 0 deg longitude and 90 deg latitude
  ## the pixel size is 0.25 degrees, so the full image is 720 pixel by 360 lines
  
  ########################################################
  # Open data
  ## raster = gdal.Open(in_file)
  
  for file in [indepthfile, indemfile]:
    ds = gdal.Open(file)
    listdatasets.append(ds)
  
  ## get data type
  datatype = listdatasets[0].GetRasterBand(1).DataType
  
  # Create for target raster the same projection as for the value raster
  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt(listdatasets[0].GetProjectionRef())
  
  ## Find the overlap between the images
  
  ## Get bounds of each image
  listbounds = []
  
  Xres = (listdatasets[0].GetGeoTransform())[1]
  Yres = (listdatasets[0].GetGeoTransform())[5]
  
  for ds in listdatasets:
    gt = ds.GetGeoTransform()
    # r has left, top, right, bottom of datasets's bounds in geospatial coordinates.
    r = [gt[0], gt[3], gt[0] + (gt[1] * ds.RasterXSize), gt[3] + (gt[5] * ds.RasterYSize)]
    listbounds.append(r)
  
  minx = np.double(100000000.)
  maxx = np.double(-100000000.)
  miny = np.double(100000000.)
  maxy = np.double(-100000000.)
  
  for bnd in listbounds:
    if (bnd[0] < minx): minx = bnd[0]
    if (bnd[1] > maxy): maxy = bnd[1]
    if (bnd[2] > maxx): maxx = bnd[2]
    if (bnd[3] < miny): miny = bnd[3]
  
  minx = np.floor(minx/Xres) * Xres
  maxx = np.ceil(maxx/Xres) * Xres
  miny = np.floor(miny/np.abs(Yres)) * np.abs(Yres)
  maxy = np.ceil(maxy/np.abs(Yres)) * np.abs(Yres)
  
  mosaicbounds = [minx, maxy, maxx, miny]
  mosaicXsize = int((maxx - minx)/abs(Xres)) + 1
  mosaicYsize = int((maxy - miny)/abs(Yres)) + 1
  
  offsetsx = []
  offsetsy = []
  
  for bnd in listbounds:
    offsetsx.append(int(round((bnd[0]-minx)/abs(Xres))))
    offsetsy.append(int(round((maxy-bnd[1])/abs(Yres))))
  
  ## create geotransform of mosaic bounds
  gt = listdatasets[0].GetGeoTransform()
  newgt = tuple((minx, gt[1], np.double(0.0), maxy, np.double(0.0), gt[5]))
  
  centerutm = np.zeros(2)
  centerutm[0] = (mosaicbounds[0]+mosaicbounds[2])/2. 
  centerutm[1] = (mosaicbounds[1]+mosaicbounds[3])/2. 
  print("%12.2f, %12.2f" % (centerutm[0], centerutm[1]))
  
  projutm5 = pyproj.Proj(proj="utm", zone=5, datum='WGS84')
  centerlatlon = projutm5(centerutm[0], centerutm[1], inverse=True)
  
  print("%12.7f, %12.7f" % (centerlatlon[0], centerlatlon[1]))
  
  ## if (centerlatlon[0] < 0.0):
  ##   pix = (180.0*4.0) + ((180.0+centerlatlon[0]) * 4.0)
  ## else:
  ##   pix = (centerlatlon[0] * 4.0)
  ## 
  ## if (centerlatlon[1] < 0.0):
  ##   lin = (90.0 + abs(centerlatlon[1])) * 4.0
  ## else:
  ##   lin = (90.0 - centerlatlon[1]) * 4.0
  
  egmgt = egmds.GetGeoTransform()
  
  pix = np.floor((centerlatlon[0] - egmgt[0])/egmgt[1])
  lin = np.floor((centerlatlon[1] - egmgt[3])/egmgt[5])
  
  print ("Pix: %d, Lin: %d") % (pix, lin)
   
  egmdata = egmds.GetRasterBand(1)
  egmsub = egmdata.ReadAsArray(pix-25, lin-25, 50, 50)
  
  print("%12.2f, %12.2f") % (pix-25, lin-25)
  
  memdriver = gdal.GetDriverByName('MEM')
  egmsubrast = memdriver.Create('', 50, 50, 1, gdal.GDT_Float32)
  ## ulx = np.floor(centerlatlon[0]) - (egmgt[1] * 3)
  ## uly = np.ceil(centerlatlon[1]) + (egmgt[5] * 3)
  ulx = egmgt[0] + (np.abs(egmgt[1]) * (pix-25))
  uly = egmgt[3] - (np.abs(egmgt[5]) * (lin-25))
  
  egmsubrast.SetGeoTransform((ulx, egmgt[1], 0, uly, 0, egmgt[5]))
  egmBand = egmsubrast.GetRasterBand(1)
  egmBand.WriteArray(egmsub)
  outegmSRS = osr.SpatialReference()
  outegmSRS.ImportFromEPSG(4326)
  egmsubrast.SetProjection(outegmSRS.ExportToWkt())
  egmBand.FlushCache()
  
  memdriver2 = gdal.GetDriverByName('ENVI')
  outegmutm = memdriver2.Create('outegmenvi', mosaicXsize, mosaicYsize, 1, gdal.GDT_Float32)
  outegmutm.SetGeoTransform(newgt)
  oututmSRS = osr.SpatialReference()
  oututmSRS.ImportFromEPSG(32605)
  outegmutm.SetProjection(oututmSRS.ExportToWkt())
  
  ## gdal.Warp(outegmutm, egmsubrast, dstSRS='EPSG:32605', format='ENVI', xRes=Xres, yRes=Yres, targetAlignedPixels=True, \
  ##  resampleAlg='cubicspline', outputBounds=(minx, maxy, maxx,miny))
  result = gdal.ReprojectImage(egmsubrast, outegmutm, outegmSRS.ExportToWkt(), oututmSRS.ExportToWkt(), gdal.GRA_CubicSpline)
  del outegmutm
  
  outegmutm = gdal.Open('outegmenvi')
  
  egmutmBand = outegmutm.GetRasterBand(1)
  egm = egmutmBand.ReadAsArray(0, 0, mosaicXsize, mosaicYsize)
  
  full = np.zeros((mosaicYsize, mosaicXsize), dtype=np.float32)
  blank = np.zeros((mosaicYsize, mosaicXsize), dtype=np.float32)
  
  ## put ground DEM in mosaic space
  data = listdatasets[1].GetRasterBand(1)
  full[offsetsy[1]:(offsetsy[1]+listdatasets[1].RasterYSize), offsetsx[1]:(offsetsx[1]+listdatasets[1].RasterXSize)] = \
    data.ReadAsArray(0, 0, listdatasets[1].RasterXSize, listdatasets[1].RasterYSize)
  
  blank.fill(-9999)
  
  depth = listdatasets[0].GetRasterBand(1)
  blank[offsetsy[0]:(offsetsy[0]+listdatasets[0].RasterYSize), offsetsx[0]:(offsetsx[0]+listdatasets[0].RasterXSize)] = \
    depth.ReadAsArray(0, 0, listdatasets[0].RasterXSize, listdatasets[0].RasterYSize)
  
  tempstack = np.dstack((np.not_equal(blank, 0), np.not_equal(blank, -9999.0), np.not_equal(blank, 7.0)))
  depthgood = np.all(tempstack, axis=2)
  
  blank = egm - blank
  
  full[depthgood] = blank[depthgood]
  del tempstack
  
  driver = listdatasets[0].GetDriver()
  outDs = driver.Create(outfile, mosaicXsize, mosaicYsize, 1, datatype) 
  outDs.SetGeoTransform(newgt)
  outDs.SetProjection(raster_srs.ExportToWkt())
  outBand = outDs.GetRasterBand(1)
  outBand.WriteArray(full)
  outBand.FlushCache()
  outBand.SetNoDataValue(-9999)
  
  del egmds, outegmutm, egmsubrast, outDs, outBand
  
  for ds in listdatasets:
    del ds

  os.remove('outegmenvi')

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print "[ USAGE ] you must supply 3 arguments: make_depth_dem.py indepthfile indemfile outmosaicfile"
    print ""
    sys.exit( 1 )

  print main( sys.argv[1], sys.argv[2], sys.argv[3] )
