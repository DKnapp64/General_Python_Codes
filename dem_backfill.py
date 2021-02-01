import numpy as np
import gdal, ogr, osr
import pyproj
import sys
import pdb

## def main(inutmdemfile, inroughfile, demfilled):
inutmdemfile = '/lustre/scratch/cao/OahuVSWIRTemp/stdproc/coral_oahu_kaneohe/cao3/rawlines/CAO20170905t184501p0000/CAO20170905t184501p0000_dem_mosaic'
inlatlondem = '/Volumes/DGE/CAO/caodata/support/AIG_Support_Data/hawaii_raw_dem_mos'
## egmfile = '/Volumes/DGE/CAO/caodata/support/AIG_Support_Data/egm96'
egmfile = '/Volumes/DGE/CAO/caodata/support/AIG_Support_Data/egm2008-2_5_float32'
listdatasets = []

egmds = gdal.Open(egmfile)
inutmds = gdal.Open(inutmdemfile)
inlatlonds = gdal.Open(inlatlondem)

egmgt = egmds.GetGeoTransform()
egmproj = egmds.GetProjectionRef()

## get data type
datatype = inutmds.GetRasterBand(1).DataType

# Create for target raster the same projection as for the value raster
raster_srs = osr.SpatialReference()
raster_srs.ImportFromWkt(inutmds.GetProjectionRef())
tempstring = raster_srs.GetAttrValue('PROJCS')
tempstring = tempstring[-3:]
if (tempstring[0] == '_'):
  zonenum = int(tempstring[1:2])
else:
  zonenum = int(tempstring[1:3])
if (tempstring[-1] == 'N'):
  epsgnum = 32600 + zonenum
if (tempstring[-1] == 'S'):
  epsgnum = 32700 + zonenum
  zonenum = -(zonenum)

## Get bounds of each image

ingt = inutmds.GetGeoTransform()
Xres = ingt[1]
Yres = ingt[5]

newgt = tuple(((np.floor(ingt[0]/Xres)-500)*Xres, ingt[1], np.double(0.0), (np.ceil(ingt[3]/(-Yres))+500)*(-Yres), np.double(0.0), ingt[5]))
bounds = [newgt[0], newgt[3], newgt[0]+(inutmds.RasterXSize+1000)*Xres, newgt[3]+(inutmds.RasterYSize+1000)*Yres]

## create geotransform of mosaic bounds

mosaicXsize = int((bounds[2] - bounds[0])/Xres)
mosaicYsize = int((bounds[3] - bounds[1])/Yres)

centerutm = np.zeros(2)
centerutm[0] = (bounds[0]+bounds[2])/2. 
centerutm[1] = (bounds[1]+bounds[3])/2. 
print("%12.2f, %12.2f" % (centerutm[0], centerutm[1]))

projutm = pyproj.Proj(proj="utm", zone=zonenum, datum='WGS84')
centerlatlon = projutm(centerutm[0], centerutm[1], inverse=True)

print("%12.7f, %12.7f" % (centerlatlon[0], centerlatlon[1]))

## egmdata = egmds.GetRasterBand(1)

## memdriver2 = gdal.GetDriverByName('ENVI')
## outegmutm = memdriver2.Create('egmtestout', mosaicXsize, mosaicYsize, 1, gdal.GDT_Float32)
## outegmutm.SetGeoTransform(newgt)
## oututmSRS = osr.SpatialReference()
## oututmSRS.ImportFromEPSG(epsgnum)
## outegmutm.SetProjection(oututmSRS.ExportToWkt())

memdriver2 = gdal.GetDriverByName('ENVI')
outegmutm = memdriver2.Create('outegmenvi', mosaicXsize, mosaicYsize, 1, gdal.GDT_Float32)
outegmutm.SetGeoTransform(newgt)
oututmSRS = osr.SpatialReference()
oututmSRS.ImportFromEPSG(epsgnum)
outegmutm.SetProjection(oututmSRS.ExportToWkt())

result = gdal.ReprojectImage(egmds, outegmutm, egmproj, oututmSRS.ExportToWkt(), gdal.GRA_CubicSpline)
del outegmutm


gdal.Warp('egmouttest', egmds, srcSRS=egmproj, dstSRS='EPSG:'+str(epsgnum), format='ENVI', xRes=Xres, yRes=Yres, \
  resampleAlg='cubicspline', outputBounds=(bounds[0], bounds[3], bounds[2], bounds[1]))
## gdal.Warp(outegmutm, egmds, srcSRS=egmproj, dstSRS='EPSG:'+str(epsgnum), format='ENVI', xRes=Xres, yRes=Yres, \
##   resampleAlg='cubicspline', outputBounds=(bounds[0], bounds[3], bounds[2], bounds[1]))

pdb.set_trace()

## result = gdal.ReprojectImage(egmds, outegmutm, egmds.GetProjectionRef(), oututmSRS.ExportToWkt(), gdal.GRA_CubicSpline)


egmdata = egmds.GetRasterBand(1)

memdriver2 = gdal.GetDriverByName('MEM')
outegmutm = memdriver2.Create('', mosaicXsize, mosaicYsize, 1, gdal.GDT_Float32)
outegmutm.SetGeoTransform(newgt)
oututmSRS = osr.SpatialReference()
oututmSRS.ImportFromEPSG(32604)
outegmutm.SetProjection(oututmSRS.ExportToWkt())

result = gdal.ReprojectImage(egmsubrast, outegmutm, outegmSRS.ExportToWkt(), oututmSRS.ExportToWkt(), gdal.GRA_CubicSpline)

## gdal.Warp(outegmutm, egmsubrast, dstSRS='EPSG:32604', format='MEM', xRes=Xres, yRes=Yres, targetAlignedPixels=True, \
##  resampleAlg='cubicspline', outputBounds=(minx, maxy, maxx,miny))

egmutmBand = outegmutm.GetRasterBand(1)
egm = egmutmBand.ReadAsArray(0, 0, mosaicXsize, mosaicYsize)
full = np.zeros((mosaicYsize, mosaicXsize), dtype=np.float32)
blank = np.zeros((mosaicYsize, mosaicXsize), dtype=np.float32)

## put ground DEM in mosaic space
data = listdatasets[1].GetRasterBand(1)
full[offsetsy[1]:(offsetsy[1]+listdatasets[1].RasterYSize), offsetsx[1]:(offsetsx[1]+listdatasets[1].RasterXSize)] = \
  data.ReadAsArray(0, 0, listdatasets[1].RasterXSize, listdatasets[1].RasterYSize)

blank.fill(0)

depth = listdatasets[0].GetRasterBand(1)
blank[offsetsy[0]:(offsetsy[0]+listdatasets[0].RasterYSize), offsetsx[0]:(offsetsx[0]+listdatasets[0].RasterXSize)] = \
  depth.ReadAsArray(0, 0, listdatasets[0].RasterXSize, listdatasets[0].RasterYSize)

depthgood  = np.not_equal(blank, 0)
blank = egm - blank

full[depthgood] = blank[depthgood]

driver = listdatasets[0].GetDriver()
outDs = driver.Create(outfile, mosaicXsize, mosaicYsize, 1, datatype) 
outDs.SetGeoTransform(newgt)
outDs.SetProjection(raster_srs.ExportToWkt())
outBand = outDs.GetRasterBand(1)
outBand.WriteArray(full)
outBand.FlushCache()
outBand.SetNoDataValue(0)

del egmds, outegmutm, egmsubrast, outDs, outBand

for ds in listdatasets:
  del ds
