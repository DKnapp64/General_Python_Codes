#!/bin/env python3
import gdal
import osr
import numpy as np
import fnmatch, re
import datetime
import os, sys

def get_overlap_info(focal_bounds, focal_res, img_bounds, img_res):
    """This function tests for the intersection of 2 spaces defined by a focal (mosaic) 
     area and an image area.  It takes the input bounds of a focal area 
     (e.g., a map tile in UTM to mosaic), the resolution, the image bounds 
     (also in UTM) and its resolution.  It returns two tuples with the upper left
     (i.e., NorthWest) corner pixel and line (column and row), and the number 
     of columns and rows for the image area and a tuple of the same format,
     but for the coinciding mosaic area.  If there is no intersection of the 2
     spaces, it returns a tuple of four -1s.
    """

    ## focal and image bounds are in the order (Xmin, Xmax, Ymin, Ymax)
    r1 = [focal_bounds[0], focal_bounds[3], focal_bounds[1], focal_bounds[2]]
    r2 = [img_bounds[0], img_bounds[3], img_bounds[1], img_bounds[2]]
  
    ## find intersection
    intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]
  
    ## Test for non-overlap.  if not overlapping, return -1s.
    if ((intersection[0] > intersection[2]) or (intersection[3] > intersection[1])):
      return((-1.0,-1.0,-1.0,-1.0), (-1.0,-1.0,-1.0,-1.0))
      
    # check for any overlap
    left1flt = (intersection[0]-r1[0])/focal_res # difference divided by pixel dimension
    left1 = int(np.abs(round((intersection[0]-r1[0])/focal_res))) # difference divided by pixel dimension
    top1flt = round((intersection[1]-r1[1])/focal_res)
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
  
    return([left1,top1,col1,row1], [left2,top2,col2,row2])
 
def maketime(infile):
    """This function takes the name of a Planet Dove image file and 
     returns a datetime object with the date and time of the image 
     and a string with the satellite id of the image.
    """

    basedove = os.path.basename(infile)
    year = int(basedove[0:4])
    month = int(basedove[4:6])
    day = int(basedove[6:8])
    hour = int(basedove[9:11])
    minute = int(basedove[11:13])
    second = int(basedove[13:15])
      
    if (len(basedove.split('_')[2]) == 4): 
      satellite = basedove.split('_')[2] 
      hms = basedove.split('_')[1] 
    else:
      if (len(basedove.split('_')[2]) < 4): 
        satellite = basedove.split('_')[3] 
        hms = basedove.split('_')[1] 
  
    imgdate = datetime.date(year, month, day).timetuple().tm_yday
    mytime = datetime.datetime(year, month, day, hour, minute, second)
    return mytime, satellite

def mosaic_dove(indovedir, datestring, utmzone, focal_bounds):
    """This function takes an input directory name where the PlanetScope
     4-band images exist with their corresponding UDM2 masks.  It also takes a
     date string (e.g., 20190604) and teh UTM image bounds of the area to 
     be msoaicked.
     The function will search the directory for any surface reflectance
     Dove images that were collected on the day indicated in the datestring
     as well as having any overlap in the focal area.
     It returns a sorted list of the surface reflectance image files that match
     the date and overlap criteria.
    """
  
    doveroot = datestring+'*3B_AnalyticMS_SR.tif'
    doveregex = fnmatch.translate(doveroot)
    dovereobj = re.compile(doveregex)
    
    dovelist = []
    times = [] 
    sats = [] 
    
    filelist2 = os.listdir(indovedir)
    if (len(filelist2) == 0):
      return([])
    
    for dovefile in filelist2:
      gotit = dovereobj.match(dovefile)
      if gotit is not None:
        tmpDS = gdal.Open(indovedir+os.path.sep+dovefile, gdal.GA_ReadOnly)
        tmpProj = tmpDS.GetProjectionRef()
        tempOSR = osr.SpatialReference()
        tempOSR.ImportFromWkt(tmpProj)
        thisutm = tempOSR.GetUTMZone()
        if (thisutm != utmzone):
          tmpDS = None
          continue
        ## Does the file intersect area of interest?
        gt = tmpDS.GetGeoTransform()
        imgbnd = (gt[0], gt[0]+tmpDS.RasterXSize*gt[1], gt[3] + tmpDS.RasterYSize*gt[5], gt[3])
        myfocal, myimgbounds = get_overlap_info(focal_bounds, gt[1], imgbnd, gt[1])
        if (np.all(np.equal(myimgbounds, -1))):
          print("Image %s does not intersect" % (dovefile))
          tmpDS = None
          continue
        thistime, thissatellite = maketime(dovefile)
        times.append(thistime)
        sats.append(thissatellite)
        dovelist.append(indovedir+os.path.sep+dovefile)
  
    if (len(dovelist) == 0):
      return([])

    dovelist = sorted(dovelist)
    countit = 0
  
    for j,name in enumerate(dovelist):
      thistime, thissatellite = maketime(dovelist[j])
      if (countit < 1):
        mylist = [dovelist[j]]
        countit = 1
      else:
        lasttime, lastsatellite = maketime(dovelist[j-1])
        if (thistime < (lasttime + datetime.timedelta(hours=6))):
          mylist.append(dovelist[j])
          countit += 1

    return(sorted(mylist))
    
def main(dovedir, ulx, uly, lrx, lry, utmzone, datestring, outmosaic):
    """This is the main commandline function (mosaic_dove_wmask.py) 
     It takes the following UTM coordinates that define the area for wehich a 
     mosaic will be created from available images:
     ulx = upper left UTM X coordinate
     uly = upper left UTM Y coordinate
     lrx = lower right UTM X coordinate
     lry = lower right UTM Y coordinate
     utmz = UTM zone
     datestring = the date for which images will be searched (e.g., 20190604)
     outmosaic = the output mosaic file name (GeoTiff)
    """

    ulx = int(float(ulx)/3.0) * 3.0
    uly = int(float(uly)/3.0) * 3.0
    lrx = int(float(lrx)/3.0) * 3.0
    lry = int(float(lry)/3.0) * 3.0
    focal_bounds = (ulx, lrx, lry, uly)
    imglist = mosaic_dove(dovedir, datestring, utmzone, focal_bounds)
    if (len(imglist) == 0):
      print("%s : No images found that match." % (datestring))
      sys.exit(0)
    
    ## create mosaic
    tmpDS = gdal.Open(imglist[0], gdal.GA_ReadOnly)
    theproj = osr.SpatialReference()
    theproj.ImportFromWkt(tmpDS.GetProjectionRef())
    tgt = tmpDS.GetGeoTransform()
    drv = gdal.GetDriverByName("GTiff")
    xsize = int((lrx - ulx)/tgt[1])
    ysize = int((lry - uly)/tgt[5])
    numBands = tmpDS.RasterCount
    mosDS = drv.Create(outmosaic, xsize, ysize, numBands, tmpDS.GetRasterBand(1).DataType, [ 'COMPRESS=LZW' ] )
    mosDS.SetGeoTransform((ulx, tgt[1], 0, uly, 0, tgt[5]))
    mosDS.SetProjection(theproj.ExportToWkt())
    tmpDS = None 

    ## make blank bands for mosaic
    blank1 = np.zeros((ysize, xsize), dtype=np.int16)
    blank2 = np.zeros((ysize, xsize), dtype=np.int16)
    blank3 = np.zeros((ysize, xsize), dtype=np.int16)
    blank4 = np.zeros((ysize, xsize), dtype=np.int16)
    mosbands = [blank1, blank2, blank3, blank4]

    for img in imglist:
      print("%s" % (img))
      maskname = img[0:-18] + '_udm2.tif'

      try:
        inDS = gdal.Open(img, gdal.GA_ReadOnly)
      except:
        print("Cannot open file %s, skipping" % (img))
        continue

      gt = inDS.GetGeoTransform()
      iulx = gt[0] 
      iuly = gt[3] 
      ilrx = gt[0] + (inDS.RasterXSize * gt[1])
      ilry = gt[3] + (inDS.RasterYSize * gt[5])
      img_bounds = (iulx, ilrx, ilry, iuly)

      if (os.path.exists(maskname)):
        maskDS = gdal.Open(maskname, gdal.GA_ReadOnly)
        mgt = maskDS.GetGeoTransform()
        mulx = mgt[0] 
        muly = mgt[3] 
        mlrx = mgt[0] + (maskDS.RasterXSize * mgt[1])
        mlry = mgt[3] + (maskDS.RasterYSize * mgt[5])
        mask_bounds = (mulx, mlrx, mlry, muly)
        thefmbnds, thembnds = get_overlap_info(focal_bounds, tgt[1], mask_bounds, mgt[1])
        thefibnds, theibnds = get_overlap_info(focal_bounds, tgt[1], img_bounds, gt[1])

        if (np.all(np.equal(thefibnds, thefmbnds))):
          thefbnds = thefibnds
        else:
          col = max(thefibnds[0],thefmbnds[0]) 
          row = max(thefibnds[1],thefmbnds[1]) 
          ncol = min(thefibnds[2],thefmbnds[2])-1 
          nrow = min(thefibnds[3],thefmbnds[3])-1 
          thefbnds = (col, row, ncol, nrow)
          theibnds = (theibnds[0], theibnds[1], ncol, nrow)
          thembnds = (thembnds[0], thembnds[1], ncol, nrow)

        maskdata = maskDS.GetRasterBand(1).ReadAsArray(thembnds[0], thembnds[1], thembnds[2], thembnds[3])
        confdata = maskDS.GetRasterBand(7).ReadAsArray(thembnds[0], thembnds[1], thembnds[2], thembnds[3])
        maskdata = maskdata.astype(bool)
        confdata = np.greater(confdata, 70)
        maskconf = np.logical_and(maskdata, confdata)

      else:
        thefibnds, theibnds = get_overlap_info(focal_bounds, tgt[1], img_bounds, gt[1])
        thefbnds = thefibnds
        print("Mask image %s not found." % (maskname))
        maskconf = np.ones((theibnds[3],theibnds[2]), dtype=bool) 

      imgdata = inDS.GetRasterBand(1).ReadAsArray(theibnds[0], theibnds[1], theibnds[2], theibnds[3])
      imgdata = np.greater(imgdata, 0)

      both = np.logical_and(maskconf, imgdata)
      indy, indx = np.indices(imgdata.shape)
      iindx = indx[both]
      iindy = indy[both]
      findx = indx[both] + thefbnds[0]
      findy = indy[both] + thefbnds[1]

      ## for each band, extract and place in mosaic
      for band in range(inDS.RasterCount):
        bdata = inDS.GetRasterBand(band+1).ReadAsArray(theibnds[0], theibnds[1], theibnds[2], theibnds[3])
        mosbands[band][findy,findx] = bdata[iindy,iindx]

      inDS, maskDS = None, None
       
   ## After all bands from all files are written, save the mosaic bands to the output file.
    for band in range(numBands):
      mosDS.GetRasterBand(band+1).WriteArray(mosbands[band])
      mosDS.GetRasterBand(band+1).SetNoDataValue(0)

    mosDS = None
    
    
if __name__ == "__main__":

  if len( sys.argv ) != 9:
    print("[ ERROR ] you must supply 8 arguments: mosaic_dove_wmasks.py dovedir ulx uly lrx lry utmzone datestring outmosaic")
    print("    dovedir = directory containing the Dove images (*_SR.tif) to get parameters for.")
    print("    ulx uly lrx lry = the upper left and lower right X and Y coordinates to subset the mosaic to.")
    print("    utmzone = the UTM zone (positive is North, negative is South)")
    print("    datestring = the date to collect images for the mosaic (e.g., 20190604)")
    print("    outmosaic = the output mosaic image file")
    print("")

    sys.exit( 0 )

  main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6]), sys.argv[7], sys.argv[8])
