#!/bin/env python3
import sys
import os
from planet import api
from planet.api import downloader
import gdal, ogr, osr
import numpy as np
import matplotlib.pyplot as plt
import pyproj
import scipy.misc as sp
import utm
import copy
import csv
import fnmatch
from myrgb2hsv import myrgb2hsv
from getchla import getchla
from depth import depth
from rb import rb
import subprocess

def get_overlap_info(focal_bounds, focal_res, img_bounds, img_res):

  ##                X_min      X_max     Y_min     Y_max
  ## Bounding Box: 436933.02 449804.48 1922102.98 1928663.29 
  ## find bounds of images
  ## r1 = [new_geo[0], new_geo[3], new_geo[0] + (new_geo[1] * dest.RasterXSize), new_geo[3] + (new_geo[5] * dest.RasterYSize)]
  ## r2 = [gt2[0], gt2[3], gt2[0] + (gt2[1] * img2.RasterXSize), gt2[3] + (gt2[5] * img2.RasterYSize)]
 
  r1 = [focal_bounds[0], focal_bounds[3], focal_bounds[1], focal_bounds[2]]
  r2 = [img_bounds[0], img_bounds[3], img_bounds[1], img_bounds[2]]
  ## find intersection
  intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]
  ## pdb.set_trace() 
  ## testx = intersection[3]-intersection[0]
  ## testy = intersection[3]-intersection[0]

  # check for any overlap
  left1flt = (intersection[0]-r1[0])/focal_res # difference divided by pixel dimension
  left1 = int(np.abs(round((intersection[0]-r1[0])/focal_res))) # difference divided by pixel dimension
  top1flt = (intersection[1]-r1[1])/focal_res
  top1 = int(np.abs(round(((intersection[1]-r1[1])/focal_res))))
  col1 = int(np.abs(round(((intersection[2]-r1[0])/focal_res) - left1flt))) # difference minus offset left
  row1 = int(np.abs(round(((intersection[3]-r1[1])/focal_res) - top1flt)))
 
  left2flt = (intersection[0]-r2[0])/img_res # difference divided by pixel dimension
  left2 = int(np.abs(round(((intersection[0]-r2[0])/img_res)))) # difference divided by pixel dimension
  top2flt = (intersection[1]-r2[1])/img_res
  top2 = int(np.abs(round(((intersection[1]-r2[1])/img_res))))
  col2 = int(np.abs(round(((intersection[2]-r2[0])/img_res) - left2flt))) # difference minus new left offset
  row2 = int(np.abs(round(((intersection[3]-r2[1])/img_res) - top2flt)))
 
  ## print("%d   %d    %d   %d" % (left1,top1,col1,row1))
  ## print("%d   %d    %d   %d" % (left2,top2,col2,row2))

  return((left1,top1,col1,row1), (left2,top2,col2,row2))
 
def download_planet(ullatlon, lrlatlon, outputdir):
  client = api.ClientV1()

  aoi = {
    "type": "Polygon",
    "coordinates": [
      [
        [float(ullatlon[0]), float(ullatlon[1])],
        [float(lrlatlon[0]), float(ullatlon[1])],
        [float(lrlatlon[0]), float(lrlatlon[1])],
        [float(ullatlon[0]), float(lrlatlon[1])],
        [float(ullatlon[0]), float(ullatlon[1])],
      ]
    ]
  }

  query = api.filters.and_filter(api.filters.geom_filter(aoi), \
    api.filters.range_filter('cloud_cover', lt=0.1), \
    api.filters.date_range('acquired', gt='2016-08-01', lt='2016-09-30'))

  item_types = ['PSScene4Band']
  request = api.filters.build_search_request(query, item_types)

  results = client.quick_search(request)

  myreps = []

  for item in results.items_iter(limit=100):
    ## sys.stdout.write(r'%s\n' % item['id'])
    print(r'%s' % item['id'])
    myreps.append(item)

  mydownloader = downloader.create(client)

  print((r'Starting Download of %d images.') % len(myreps))
  mydownloader.download(results.items_iter(len(myreps)), ['analytic','analytic_xml'], outputdir)
  mydownloader.shutdown()
  print(('Finished with Download.'))
  return( 0 )

def main( ulx, uly, lrx, lry, outputdir ):
  ullatlon = []
  lrlatlon = []
  ullatlon.append(ulx) 
  ullatlon.append(uly) 
  lrlatlon.append(lrx) 
  lrlatlon.append(lry) 

  ## done = download_planet(ullatlon, lrlatlon, outputdir)

  ##  check to see how many files are there
  imglist = []
  rawlist = os.listdir(outputdir)

  for filename in rawlist:
    if (os.path.isfile(outputdir+filename) and fnmatch.fnmatch(filename, '*_AnalyticMS.tif')):
      imglist.append(filename) 

  numimgs = len(imglist)

  ## add stuff to build reflectance lookup tables and apply them
##   success = subprocess.call(["extract_atmos_params_spatial_interp.py", outputdir, outputdir+"atmos_params.csv"])
##   
  f = open(outputdir+"atmos_params.csv", 'r')
  x = f.readlines()
  f.close()
## 
##   for row in x:
##     vals = row.split(',')
##     success = subprocess.call(["generate_rad_to_refl_lut.py", outputdir+vals[0].strip(), vals[1].strip(), vals[2].strip(), vals[3].strip(), outputdir])
## 
  refllist = []
## 
##   ## for each image, apply its lut to make reflectance image
## 
  for row in x:
    vals = row.split(',')
    inradfile = os.path.join(outputdir, vals[0].strip())
    inlutfile = os.path.join(outputdir, vals[0].split('.')[0]+"_luts.npz")
    outreflfile = os.path.join(outputdir, vals[0].split('.')[0]+"_refl")
    refllist.append(outreflfile)
##     success = subprocess.call(["apply_refl_lut.py", inradfile, inlutfile, outreflfile])
## 
  drv = gdal.GetDriverByName('GTiff')

  ## for each reflectance image run the steps to get depth and bottom reflectance

  ## make and empty list that is same length to hold Chla values
  chlavals = [None] * len(refllist)

  for i,infile in enumerate(refllist):

    outhsvfile = os.path.splitext(os.path.basename(infile.strip()))[0]+'_hsv'  
    depthfile = os.path.splitext(infile)[0][0:-5] + "_depth.tif"
    rbfile = os.path.splitext(infile)[0][0:-5] + "_rb.tif"

    myrgb2hsv(infile, outhsvfile) 
    print(("Processed RGB to HSV: %s") % (infile))
    chlavals[i] = getchla(outhsvfile, infile)
    print(("Chla: %7.4f for %s") % (chlavals[i], infile))

    if (os.path.isfile(outhsvfile)):
      os.remove(outhsvfile)
    if (os.path.isfile(outhsvfile+".hdr")):
      os.remove(outhsvfile+".hdr")

    ## filter out an Nans, negatives and values > 1.0 to get valid Chl-a values
    ## good1 = np.less(chlavals, 1.0)
    ## good2 = np.greater(chlavals, 0.0)
    ## good3 = np.logical_not(np.isnan(chlavals))
    ## goodchla = np.all(np.stack((good1, good2, good3)), axis=0)

    try:
      chla_global = chlavals[i]
    except ValueError:
      print("Problem with value in Chl-a array.")

    print(("\n%s   Chla for: %7.4f\n") % (infile, chla_global))

    try:
      depth(infile, chla_global, depthfile)
    except:
      print("Error: Could not create Depth data.")
      continue

    print(("Processed Depth: %s") % (depthfile))

    if (os.path.isfile(depthfile)): 
      try:
        rb(infile, chla_global, depthfile, rbfile)
      except:
        print("Error: Could not create Rb data.")
        continue
    else: 
      print(("Error: Could not find depth data file %s, so could not do bottom reflectance.") % (depthfile))
      continue

    print(("Processed Bottom Reflectance: %s") % (rbfile))

    print(("%d") % (i))
    if (os.path.isfile(infile)):
      # Open data
      rasterDS = gdal.Open(infile, gdal.GA_ReadOnly)
    else:
      print(("File: %s does not exist....skipping") % (outputdir+infile))
      continue
  
    # Get raster georeference info
    gt = rasterDS.GetGeoTransform()
    xOrigin = gt[0]
    yOrigin = gt[3]
    pixelWidth = gt[1]
    pixelHeight = gt[5]
  
    img_bounds = (gt[0], gt[0]+(rasterDS.RasterXSize*gt[1]), gt[3]+(rasterDS.RasterYSize*gt[5]), gt[3])

    x1, y1 =  utm.from_latlon(ullatlon[1], ullatlon[0])[0:2]
    x2, y2 =  utm.from_latlon(lrlatlon[1], ullatlon[0])[0:2]
    x3, y3 =  utm.from_latlon(lrlatlon[1], lrlatlon[0])[0:2]
    x4, y4 =  utm.from_latlon(ullatlon[1], lrlatlon[0])[0:2]
    xmin = min([x1, x2, x3, x4])
    xmax = max([x1, x2, x3, x4])
    ymin = min([y1, y2, y3, y4])
    ymax = max([y1, y2, y3, y4])

    focal_bounds = (xmin, xmax, ymin, ymax) 

    (focalinfo, imginfo) = get_overlap_info(focal_bounds, gt[1], img_bounds, gt[1])

    # Specify offset and rows and columns to read
    xoff = int((xmin - xOrigin)/pixelWidth)
    yoff = int((ymax - yOrigin)/pixelHeight)
    xcount = int((xmax - xmin)/pixelWidth)+1
    ycount = int((ymin - ymax)/pixelHeight)+1
  
    ## check to make sure we don't go out of bounds on image
    ## if (xoff < 0) or (yoff < 0) or ((xcount+xoff) > rasterDS.RasterXSize) or ((ycount+yoff) > rasterDS.RasterYSize):
    ##   print("Skipping %s out of bounds for this polygon"% (infile))
    ##   continue
  
    ncols = rasterDS.RasterXSize
    nrows = rasterDS.RasterYSize
  
    ## subset the water-leaving reflectance file
    outDS = drv.Create(os.path.splitext(infile)[0]+"_subset.tif", xsize=xcount, \
      ysize=ycount, bands=rasterDS.RasterCount, eType=rasterDS.GetRasterBand(1).DataType)

    outDS.SetGeoTransform((xmin, gt[1], gt[2], ymax, gt[4], gt[5]))
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(rasterDS.GetProjectionRef())
    outDS.SetProjection(outRasterSRS.ExportToWkt())

    for bandnum in range(1,5):
      thisBand = rasterDS.GetRasterBand(bandnum)
      thisData = thisBand.ReadAsArray(imginfo[0], imginfo[1], imginfo[2], imginfo[3])
      outBand = outDS.GetRasterBand(bandnum)
      outBand.WriteArray(thisData)
      outBand.FlushCache()
      del outBand

    inDS = None
    outDS = None
    rasterDS = None

    ## subset the bottom reflectance file

    if (os.path.isfile(rbfile)):
      # Open data
      rasterDS = gdal.Open(rbfile, gdal.GA_ReadOnly)
    else:
      print(("File: %s does not exist....skipping") % (outputdir+rbfile))
      continue
  
    rbDS = drv.Create(os.path.splitext(rbfile)[0]+"_subset.tif", xsize=xcount, \
      ysize=ycount, bands=rasterDS.RasterCount, eType=rasterDS.GetRasterBand(1).DataType)

    rbDS.SetGeoTransform((xmin, gt[1], gt[2], ymax, gt[4], gt[5]))
    rbDS.SetProjection(outRasterSRS.ExportToWkt())

    for bandnum in range(1,4):
      thisBand = rasterDS.GetRasterBand(bandnum)
      thisData = thisBand.ReadAsArray(imginfo[0], imginfo[1], imginfo[2], imginfo[3])
      outBand = rbDS.GetRasterBand(bandnum)
      outBand.WriteArray(thisData)
      outBand.FlushCache()
      del outBand

    rasterDS = None
    rbDS = None

    ## subset the depth file

    if (os.path.isfile(depthfile)):
      # Open data
      rasterDS = gdal.Open(depthfile, gdal.GA_ReadOnly)
    else:
      print(("File: %s does not exist....skipping") % (outputdir+depthfile))
      continue
  
    depthDS = drv.Create(os.path.splitext(depthfile)[0]+"_subset.tif", xsize=xcount, \
      ysize=ycount, bands=1, eType=gdal.GDT_Float32)

    depthDS.SetGeoTransform((xmin, gt[1], gt[2], ymax, gt[4], gt[5]))
    depthDS.SetProjection(outRasterSRS.ExportToWkt())

    thisBand = rasterDS.GetRasterBand(1)
    thisData = thisBand.ReadAsArray(imginfo[0], imginfo[1], imginfo[2], imginfo[3])
    outBand = depthDS.GetRasterBand(1)
    outBand.WriteArray(thisData)
    outBand.FlushCache()
    del outBand

    rasterDS = None
    depthDS = None


if __name__ == "__main__":

  if len( sys.argv ) != 6:
    print("[ ERROR ] you must supply 5 arguments: make_stack_widget.py ulx uly lrx lry downloaddir")
    print("where:")
    print("         ulx = the upper left X coordinate of the area to subset.")
    print("         uly = the upper left Y coordinate of the area to subset.")
    print("         lrx = the lower right X coordinate of the area to subset.")
    print("         lry = the lower right Y coordinate of the area to subset.")
    print("         downloaddir = the directory name in which to download the data.")
    print("")

    sys.exit( 1 )

  main( float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5] )
