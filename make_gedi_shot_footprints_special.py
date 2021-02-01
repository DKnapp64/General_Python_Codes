#!/bin/env python3
import os, sys
import ogr, osr
import pyproj
import numpy as np
import math

def main(inshp, outshp):

  if not os.path.exists(inshp):
    print('File %s does not exist' % (inshp))
    sys.exit(0)

  intchfile = 'all_20200716_tch_shots_sorted.txt'
  ingrndfile = 'all_20200716_grnd_shots_sorted.txt'
  inslopefile = 'all_20200716_slope_shots_sorted.txt'

  f = open(intchfile, 'r')
  inlines = f.readlines()
  f.close()

  fgrnd = open(ingrndfile, 'r')
  grndlines = fgrnd.readlines()
  fgrnd.close()

  fslope = open(inslopefile, 'r')
  slopelines = fslope.readlines()
  fslope.close()

  tchnumlines = len(inlines) - 1 
  inlines = inlines[1:]
  grndnumlines = len(grndlines) - 1 
  grndlines = grndlines[1:]
  slopenumlines = len(slopelines) - 1 
  slopelines = slopelines[1:]

  shotnumtch = np.zeros(tchnumlines, dtype=np.int64)
  fcov25 = np.zeros(tchnumlines, dtype=np.float32) 
  fcov50 = np.zeros(tchnumlines, dtype=np.float32) 
  tch25meanvals = np.zeros(tchnumlines, dtype=np.float32) 
  tch25sdevvals = np.zeros(tchnumlines, dtype=np.float32) 
  tch25modevals = np.zeros(tchnumlines, dtype=np.float32) 
  ntch25 = np.zeros(tchnumlines, dtype=np.int16) 
  tch50meanvals = np.zeros(tchnumlines, dtype=np.float32) 
  tch50sdevvals = np.zeros(tchnumlines, dtype=np.float32) 
  tch50modevals = np.zeros(tchnumlines, dtype=np.float32) 
  ntch50 = np.zeros(tchnumlines, dtype=np.int16) 
  shotnumgrnd = np.zeros(grndnumlines, dtype=np.int64)
  grnd25meanvals = np.zeros(grndnumlines, dtype=np.float32) 
  grnd25sdevvals = np.zeros(grndnumlines, dtype=np.float32) 
  grnd25modevals = np.zeros(grndnumlines, dtype=np.float32) 
  ngrnd25 = np.zeros(grndnumlines, dtype=np.int16) 
  grnd50meanvals = np.zeros(grndnumlines, dtype=np.float32) 
  grnd50sdevvals = np.zeros(grndnumlines, dtype=np.float32) 
  grnd50modevals = np.zeros(grndnumlines, dtype=np.float32) 
  ngrnd50 = np.zeros(grndnumlines, dtype=np.int16) 
  shotnumslope = np.zeros(slopenumlines, dtype=np.int64)
  slope25meanvals = np.zeros(slopenumlines, dtype=np.float32) 
  slope25sdevvals = np.zeros(slopenumlines, dtype=np.float32) 
  slope25modevals = np.zeros(slopenumlines, dtype=np.float32) 
  nslope25 = np.zeros(slopenumlines, dtype=np.int16) 
  slope50meanvals = np.zeros(slopenumlines, dtype=np.float32) 
  slope50sdevvals = np.zeros(slopenumlines, dtype=np.float32) 
  slope50modevals = np.zeros(slopenumlines, dtype=np.float32) 
  nslope50 = np.zeros(slopenumlines, dtype=np.int16) 

  for k,thisline in enumerate(inlines):
    vals = thisline.split(',')
    shotnumtch[k] = int(vals[0])
    fcov25[k] = float(vals[3])
    fcov50[k] = float(vals[4])
    tch25meanvals[k] = float(vals[5])
    tch25sdevvals[k] = float(vals[6])
    tch25modevals[k] = float(vals[7])
    ntch25[k] = int(vals[8])
    tch50meanvals[k] = float(vals[9])
    tch50sdevvals[k] = float(vals[10])
    tch50modevals[k] = float(vals[11])
    ntch50[k] = int(vals[12])

  for k,thisline in enumerate(grndlines):
    vals = thisline.split(',')
    shotnumgrnd[k] = int(vals[0])
    grnd25meanvals[k] = float(vals[3])
    grnd25sdevvals[k] = float(vals[4])
    grnd25modevals[k] = float(vals[5])
    ngrnd25[k] = int(vals[6])
    grnd50meanvals[k] = float(vals[7])
    grnd50sdevvals[k] = float(vals[8])
    grnd50modevals[k] = float(vals[9])
    ngrnd50[k] = int(vals[10])

  for k,thisline in enumerate(slopelines):
    vals = thisline.split(',')
    shotnumslope[k] = int(vals[0])
    slope25meanvals[k] = float(vals[3])
    slope25sdevvals[k] = float(vals[4])
    slope25modevals[k] = float(vals[5])
    nslope25[k] = int(vals[6])
    slope50meanvals[k] = float(vals[7])
    slope50sdevvals[k] = float(vals[8])
    slope50modevals[k] = float(vals[9])
    nslope50[k] = int(vals[10])

  pseudomerc = pyproj.Proj(init='epsg:3857')

  vecDS = ogr.Open(inshp)                                                     
  lyr = vecDS.GetLayer()                                                        
  lyrdefn = lyr.GetLayerDefn()
  fieldcnt = lyrdefn.GetFieldCount()
  sourceSR = lyr.GetSpatialRef()

  tempfeat = lyr.GetNextFeature()
  tmpgeom = tempfeat.GetGeometryRef()

  if (tmpgeom.GetGeometryName() != 'POINT'):
    print('This is not a Point shapefile: %s' % (tmpgeom.GetGeometryName()))
    vecDS.Destroy()
    sys.exit(0)

  lyr.ResetReading()

  fieldname = []
  fieldtypecode = []
  fieldtype = []
  fieldwidth = []
  fieldprecision = []

  for j in range(fieldcnt):
    fieldname.append(lyrdefn.GetFieldDefn(j).GetName())
    fieldtypecode.append(lyrdefn.GetFieldDefn(j).GetType())
    fieldtype.append(ogr.GetFieldTypeName(fieldtypecode[j]))
    fieldwidth.append(lyrdefn.GetFieldDefn(j).GetWidth())
    fieldprecision.append(lyrdefn.GetFieldDefn(j).GetPrecision())
    print(fieldname[j], fieldtypecode[j], fieldtype[j], fieldwidth[j], fieldprecision[j])

  fieldtypecode[0] = 0
  fieldtype[0] = 'Integer'
  fieldwidth[0] = 5
  fieldprecision[0] = 0
  fieldtypecode[2] = 0
  fieldtype[2] = 'Integer'
  fieldwidth[2] = 5
  fieldprecision[2] = 0
  fieldtypecode[45] = 0
  fieldtype[45] = 'Integer'
  fieldwidth[45] = 5
  fieldprecision[45] = 0
  fieldtypecode[48] = 0
  fieldtype[48] = 'Integer'
  fieldwidth[48] = 5
  fieldprecision[48] = 0

  fieldname.append('FCOV25')
  fieldname.append('FCOV50')
  fieldname.append('TCH25MEAN')
  fieldname.append('TCH25SDEV')
  fieldname.append('TCH25MODE')
  fieldname.append('NTCH25M')
  fieldname.append('TCH50MEAN')
  fieldname.append('TCH50SDEV')
  fieldname.append('TCH50MODE')
  fieldname.append('NTCH50M')
  fieldname.append('GRND25MEAN')
  fieldname.append('GRND25SDEV')
  fieldname.append('GRND25MODE')
  fieldname.append('NGRND25M')
  fieldname.append('GRND50MEAN')
  fieldname.append('GRND50SDEV')
  fieldname.append('GRND50MODE')
  fieldname.append('NGRND50M')
  fieldname.append('SLOP25MEAN')
  fieldname.append('SLOP25SDEV')
  fieldname.append('SLOP25MODE')
  fieldname.append('NSLOP25M')
  fieldname.append('SLOP50MEAN')
  fieldname.append('SLOP50SDEV')
  fieldname.append('SLOP50MODE')
  fieldname.append('NSLOP50M')
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(0)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(0)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(0)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(0)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(0)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(2)
  fieldtypecode.append(0)
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Integer')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Integer')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Integer')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Integer')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Integer')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Real')
  fieldtype.append('Integer')
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(5)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(5)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(5)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(5)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(5)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(12)
  fieldwidth.append(5)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(5)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(5)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(5)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(5)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(5)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(2)
  fieldprecision.append(5)

  ## fieldname = fieldname[2:]
  ## fieldtypecode = fieldtypecode[2:]
  ## fieldtype = fieldtype[2:]
  ## fieldwidth = fieldwidth[2:]
  ## fieldprecision = fieldprecision[2:]

  print('--------------------------------------------------')
  for k in range(len(fieldname)):
    print(fieldname[k], fieldtype[k], fieldtypecode[k], fieldwidth[k], fieldprecision[k])
  print('--------------------------------------------------')

  ## create array of 12 offsets to get a 25-meter diameter circle around each
  ## center point
  circpnts = []
  for i in np.arange(0, 12):
    y0 = 12.5 * math.cos((i*30.0)*math.pi/180.) 
    x0 = 12.5 * math.sin((i*30.0)*math.pi/180.)
    circpnts.append([x0, y0])
  circpnts = np.asarray(circpnts)

  ## Create output Shapefile
  mysrs = osr.SpatialReference()                                                
  mysrs.ImportFromEPSG(3857)
                                                                                
  ## create new output layer and Shapefile                                      
  drv = ogr.GetDriverByName("ESRI Shapefile")                                   
  dstDS = drv.CreateDataSource(outshp)                                        
  dst_layer = dstDS.CreateLayer("footprints", srs=mysrs)                          

  for j in range(fieldcnt+26):
    newField = ogr.FieldDefn(fieldname[j], fieldtypecode[j])
    newField.SetWidth(fieldwidth[j])
    newField.SetPrecision(fieldprecision[j])
    dst_layer.CreateField(newField)                                               

  layer_defn = dst_layer.GetLayerDefn()

  count = 0
  pointsX = []; pointsY = []
  for feat in lyr:
    geom = feat.GetGeometryRef()
    xc = geom.GetX()
    yc = geom.GetY()
    xcout, ycout = pseudomerc(xc, yc)
    newpnts = np.asarray([xcout, ycout]) + circpnts
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for j in range(circpnts.shape[0]):
      ring.AddPoint(newpnts[j,0], newpnts[j,1])
    ring.CloseRings()
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    outfeat = ogr.Feature(layer_defn)
    outfeat.SetGeometry(poly)
    outfeat.SetFID(count)
    for j in range(0, fieldcnt):
      fdata = feat.GetField(j)
      outfeat.SetField(fieldname[j], fdata)
    shot = feat.GetField('SHOT_NUMBE')
    indextch = np.equal(shotnumtch, shot)
    indexgrnd = np.equal(shotnumgrnd, shot)
    indexslope = np.equal(shotnumslope, shot)
    if (np.sum(indextch) > 0) or (np.sum(indexgrnd) > 0):
      if (np.sum(indextch) > 0):
        postch = tch25meanvals[indextch][0]
        if ((postch > 0.0) and (postch < 150.0) and (float(tch25sdevvals[indextch][0]) < 100.0)):
          outfeat.SetField('FCOV25', float(fcov25[indextch][0]))
          outfeat.SetField('FCOV50', float(fcov50[indextch][0]))
          outfeat.SetField('TCH25MEAN', float(tch25meanvals[indextch][0]))
          outfeat.SetField('TCH25SDEV', float(tch25sdevvals[indextch][0]))
          outfeat.SetField('TCH25MODE', float(tch25modevals[indextch][0]))
          outfeat.SetField('NTCH25M', int(ntch25[indextch][0]))
          outfeat.SetField('TCH50MEAN', float(tch50meanvals[indextch][0]))
          outfeat.SetField('TCH50SDEV', float(tch50sdevvals[indextch][0]))
          outfeat.SetField('TCH50MODE', float(tch50modevals[indextch][0]))
          outfeat.SetField('NTCH50M', int(ntch50[indextch][0]))
      if (np.sum(indexgrnd) > 0):
        posgrnd = grnd25meanvals[indexgrnd][0]
        if ((posgrnd > 0.0) and (posgrnd < 8000.0) and (float(grnd25sdevvals[indexgrnd][0] < 100.0))):
          outfeat.SetField('GRND25MEAN', float(grnd25meanvals[indexgrnd][0]))
          outfeat.SetField('GRND25SDEV', float(grnd25sdevvals[indexgrnd][0]))
          outfeat.SetField('GRND25MODE', float(grnd25modevals[indexgrnd][0]))
          outfeat.SetField('NGRND25M', int(ngrnd25[indexgrnd][0]))
          outfeat.SetField('GRND50MEAN', float(grnd50meanvals[indexgrnd][0]))
          outfeat.SetField('GRND50SDEV', float(grnd50sdevvals[indexgrnd][0]))
          outfeat.SetField('GRND50MODE', float(grnd50modevals[indexgrnd][0]))
          outfeat.SetField('NGRND50M', int(ngrnd50[indexgrnd][0]))
      if (np.sum(indexslope) > 0):
        posslope = slope25meanvals[indexslope][0]
        if ((posslope > 0.0) and (posslope < 100.0) and (float(slope25sdevvals[indexslope][0] < 100.0))):
          outfeat.SetField('SLOP25MEAN', float(slope25meanvals[indexslope][0]))
          outfeat.SetField('SLOP25SDEV', float(slope25sdevvals[indexslope][0]))
          outfeat.SetField('SLOP25MODE', float(slope25modevals[indexslope][0]))
          outfeat.SetField('NSLOP25M', int(nslope25[indexslope][0]))
          outfeat.SetField('SLOP50MEAN', float(slope50meanvals[indexslope][0]))
          outfeat.SetField('SLOP50SDEV', float(slope50sdevvals[indexslope][0]))
          outfeat.SetField('SLOP50MODE', float(slope50modevals[indexslope][0]))
          outfeat.SetField('NSLOP50M', int(nslope50[indexslope][0]))
    dst_layer.CreateFeature(outfeat)
    count += 1

  ## close the input and output shapefiles
  vecDS.Destroy()
  dstDS.Destroy()


if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ USAGE ] you must supply 2 arguments: make_gedi_shot_footprints_special.py inpattern outshape")
    print("")
    sys.exit( 1 )

  main( sys.argv[1], sys.argv[2] )

