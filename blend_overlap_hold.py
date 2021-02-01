#!/bin/env python2
"""Reads list of orthoed DiMAC images and mosaics them in the order listed, blending 
in the overlap area as each image is added"""

import sys, os
import numpy as np
from skimage.morphology import medial_axis, binary_closing, square
import gdal, osr
from datetime import datetime

def main(inlistfile, outname):

  inlist  = [line.rstrip() for line in open(inlistfile, "r")]
  randroot = "temp" + ("%05d" % (np.random.randint(0,99999)))

  for i in np.arange(len(inlist)-1):
    print("Working on %d" % (i+1)) 

    if (i > 0):
      reffile = randroot + ("_%03d" % (i-1))
    else:
      reffile = inlist[0]
  
    if (i != (len(inlist)-2)):
      newref = randroot + ("_%03d" % (i))
    else:
      newref = outname

    print("Files: %s\n %s\n\n" % (reffile,inlist[i+1]))
  
    inDS1 = gdal.Open(reffile, gdal.GA_ReadOnly)
    inDS2 = gdal.Open(inlist[i+1], gdal.GA_ReadOnly)
    
    geo1 = inDS1.GetGeoTransform()
    geo2 = inDS2.GetGeoTransform()
    
    ulx1 = geo1[0]
    uly1 = geo1[3]
    ulx2 = geo2[0]
    uly2 = geo2[3]
    
    lrx1 = geo1[0] + (inDS1.RasterXSize * geo1[1])
    lry1 = geo1[3] + (inDS1.RasterYSize * geo1[5])
    lrx2 = geo2[0] + (inDS2.RasterXSize * geo2[1])
    lry2 = geo2[3] + (inDS2.RasterYSize * geo2[5])
    
    ## create new array of combined size
    ulxcombo = np.minimum(ulx1, ulx2)
    ulycombo = np.maximum(uly1, uly2)
    lrxcombo = np.maximum(lrx1, lrx2)
    lrycombo = np.minimum(lry1, lry2)
    
    comboxsize = np.floor((lrxcombo - ulxcombo)/geo1[1]).astype(np.int) + 1
    comboysize = np.floor((ulycombo - lrycombo)/geo1[1]).astype(np.int) + 1
    
    combo = np.zeros((2, comboysize, comboxsize), dtype=np.uint8)
    newgt = (ulxcombo, geo1[1], geo1[2], ulycombo, geo1[4], geo1[5])
    
    ## find areas that are zeros in all 3 bands
    temp1 = inDS1.GetVirtualMemArray()
    temp2 = inDS2.GetVirtualMemArray()
    
    sumit1 = np.sum(temp1, axis=0)
    sumit2 = np.sum(temp2, axis=0)
    good1 = np.not_equal(sumit1, 0)
    good2 = np.not_equal(sumit2, 0)
    
    sumit1, sumit2 = None, None
  
    nodata1 = inDS1.GetRasterBand(1).GetNoDataValue()
    nodata2 = inDS2.GetRasterBand(1).GetNoDataValue()
    
    xoff1 = int(np.floor((ulx1 - ulxcombo)/geo1[1]))
    yoff1 = int(np.floor((ulycombo - uly1)/geo1[1]))
    xoff2 = int(np.floor((ulx2 - ulxcombo)/geo2[1]))
    yoff2 = int(np.floor((ulycombo - uly2)/geo2[1]))
    
    print("Offsets 1: %d %d" % (xoff1, yoff1))
    print("Offsets 2: %d %d" % (xoff2, yoff2))

    indices1 = np.indices((inDS1.RasterYSize, inDS1.RasterXSize))
    indices2 = np.indices((inDS2.RasterYSize, inDS2.RasterXSize))
    
    good1rows = indices1[0,:,:]
    good1cols = indices1[1,:,:]
    good1rows = good1rows[good1]
    good1cols = good1cols[good1]
    combo1rows = good1rows + yoff1
    combo1cols = good1cols + xoff1
    combo[0, combo1rows, combo1cols] = np.byte(1)
    
    good2rows = indices2[0,:,:]
    good2cols = indices2[1,:,:]
    good2rows = good2rows[good2]
    good2cols = good2cols[good2]
    combo2rows = good2rows + yoff2
    combo2cols = good2cols + xoff2
    combo[1, combo2rows, combo2cols] = np.byte(1)
    
    overlap = np.equal(np.sum(combo, axis=0), 2)
    ## overrows, overcols = np.indices((comboysize, comboxsize))
    ## overrows1 = overrows[overlap] - yoff1
    ## overcols1 = overcols[overlap] - xoff1
    ## overrows2 = overrows[overlap] - yoff2
    ## overcols2 = overcols[overlap] - xoff2
    
    ## try cross-shaped structuring element
    strucelem = np.zeros((101,101), dtype=np.bool)
    strucelem[50,:] = True
    strucelem[:,50] = True
    
    driver = gdal.GetDriverByName("ENVI")
    
    start_closing = datetime.now()
    img1_closed = binary_closing(good1, selem=strucelem)
    end_closing = datetime.now()
    diff = end_closing - start_closing
    print("")
    print("Finished #1 binary_closing in: %d hours %d minutes %d seconds" % \
      (diff.total_seconds()//3600, diff.total_seconds()//60 - diff.total_seconds()//3600 * 60, diff.seconds % 60))
    
    start_closing = datetime.now()
    img2_closed = binary_closing(good2, selem=strucelem)
    end_closing = datetime.now()
    diff = end_closing - start_closing
    print("Finished #2 binary_closing in: %d hours %d minutes %d seconds" % \
      (diff.total_seconds()//3600, diff.total_seconds()//60 - diff.total_seconds()//3600 * 60, diff.seconds % 60))
    
    start_medial = datetime.now()
    medaxis1, meddistance1 = medial_axis(img1_closed, return_distance=True)
    end_medial = datetime.now()
    diff = end_medial - start_medial
    print("Finished #1 medial in: %d hours %d minutes %d seconds" % \
      (diff.total_seconds()//3600, diff.total_seconds()//60 - diff.total_seconds()//3600 * 60, diff.seconds % 60))
    
    start_medial = datetime.now()
    medaxis2, meddistance2 = medial_axis(img2_closed, return_distance=True)
    end_medial = datetime.now()
    diff = end_medial - start_medial
    print("Finished #2 medial in: %d hours %d minutes %d seconds" % \
      (diff.total_seconds()//3600, diff.total_seconds()//60 - diff.total_seconds()//3600 * 60, diff.seconds % 60))
    print("")
    
    medaxis1 = None
    medaxis2 = None
    
    combodist = np.zeros((2, comboysize, comboxsize), dtype=np.float32)
    
    combodist[0, combo1rows, combo1cols] = meddistance1[good1]
    combodist[1, combo2rows, combo2cols] = meddistance2[good2]
    
    meddistance1, meddistance2 = None, None

    overlapy, overlapx = np.indices((comboysize, comboxsize))
    overlapy = overlapy[overlap]
    overlapx = overlapx[overlap]
    
    sumdist = np.sum(combodist, axis=0)
    props = np.zeros_like(combodist)
    props[0,combo1rows, combo1cols] = 1.0
    props[1,combo2rows, combo2cols] = 1.0
    props[0,overlapy,overlapx] = combodist[0,overlapy,overlapx]/sumdist[overlapy,overlapx]
    props[1,overlapy,overlapx] = combodist[1,overlapy,overlapx]/sumdist[overlapy,overlapx]
    
    outDS4 = driver.Create(newref, xsize=comboxsize, ysize=comboysize, bands=3, eType=gdal.GDT_Byte)
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(inDS1.GetProjectionRef())
    outDS4.SetProjection(raster_srs.ExportToWkt())
    outDS4.SetGeoTransform(newgt)
    
    for f in np.arange(3):
      outband = np.zeros((comboysize,comboxsize), dtype=np.uint8)
      outband[combo1rows, combo1cols] = temp1[f,good1rows,good1cols]
      outband[combo2rows, combo2cols] = temp2[f,good2rows,good2cols]
      outband[overlapy, overlapx] = temp1[f,overlapy-yoff1,overlapx-xoff1] * props[0,overlapy,overlapx] + \
                                    temp2[f,overlapy-yoff2,overlapx-xoff2] * props[1,overlapy,overlapx]
      outDS4.GetRasterBand(f+1).WriteArray(outband)
      print("Finished Blended Band %d" % (f+1))
      del outband
 
    combodist, props = None, None
    
    print("Completed Mosaic file on this iteration: %s\n" % (newref))

    temp1 = None
    temp2 = None
    outDS4 = None
    inDS1 = None
    inDS2 = None


if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print "[ USAGE ] you must supply 2 arguments: blend_overlap.py inlist outmosaic"
    print "          where:"
    print "                 inlist = text list of orthoed input DiMAC images for mosaic"
    print "                 outmosaic = output blended mosaic image"
    print ""
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2] )
