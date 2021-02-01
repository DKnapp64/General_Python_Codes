import gdal, ogr, osr
import numpy as np

def GetSpectralWavelengths(inds):
  ''' Return list of wavelengths from ENVI header 

  '''
  ext=[]
  metalist = inds.GetMetadata_List()
  ## tempwaves = np.zeros(length(metalist)-1, dtype=np.float32)
  tempwaves = []

  for i in np.arange(len(metalist)):
    t1 = metalist[i].split("=")[1].split(" ")[0]
    try:
      t1float = float(t1)
      success = 1
    except:
      success = 0

    if (success == 1):
      tempwaves.append(t1float)

  waves = np.sort(tempwaves)
  return waves


def GetExtent(inds):
  ''' Return list of corner coordinates from a geotransform

      @type inds:   C{GeoDataSet}
      @param inds: geodataset
      @rtype:    C{[float,...,float]}
      @return:   coordinates of each corner
  '''
  ext=[]
  xarr=[0,inds.RasterXSize]
  yarr=[0,inds.RasterYSize]

  gt = inds.GetGeoTransform()

  for px in xarr:
    for py in yarr:
      x=gt[0]+(px*gt[1])+(py*gt[2])
      y=gt[3]+(px*gt[4])+(py*gt[5])
      ext.append([x,y])
    yarr.reverse()
  return np.asarray(ext).T

def GetExtentFromGeom(ingeom):
  ''' Return 4 corners of extent from the geometry of a feature

      @type ingeom:   C{ogr.Geometry}
      @param ingeom: geometry
      @rtype:    C{[float,...,float]}
      @return:   coordinates of each corner
  '''

  x = [ingeom.GetGeometryRef(0).GetX(i) for i in range(ingeom.GetGeometryRef(0).GetPointCount())]
  y = [ingeom.GetGeometryRef(0).GetY(i) for i in range(ingeom.GetGeometryRef(0).GetPointCount())]

  r = {'minx': np.min(x), 'miny':np.min(y), 'maxx': np.max(x), 'maxy':np.max(y)}
  ext = [[r['minx'],r['maxy']], [r['minx'],r['miny']], [r['maxx'], r['miny']], [r['maxx'], r['maxy']]]
  return np.asarray(ext).T

def Extent2Geom(ext):
  ''' Return Geometry object from 4 corners of extent.

      @type ext:   C{np.Array}
      @param ext:   extent
      @rtype:  C{POLYGON ...}
      @return: a POLYGON geometry in WKT format
  '''
  r = {'minx': np.min(ext[0,:]), 'miny':np.min(ext[1,:]), 'maxx': np.max(ext[0,:]), 'maxy':np.max(ext[1,:])}
  template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
  w = template % r
  return w

def Coord2RowCol(gt,corners):
  ''' Convert the 4 corners of an area to the Column, Row, NumCols, NumRows format for gdal.ReadAsArray()
  '''
  ulcol = np.floor((corners[0,0] - gt[0])/gt[1]).astype(np.int)
  ulrow = np.floor((corners[1,0] - gt[3])/gt[5]).astype(np.int)
  llcol = np.floor((corners[0,1] - gt[0])/gt[1]).astype(np.int)
  llrow = np.ceil((corners[1,1] - gt[3])/gt[5]).astype(np.int)
  lrcol = np.ceil((corners[0,2] - gt[0])/gt[1]).astype(np.int)
  lrrow = np.ceil((corners[1,2] - gt[3])/gt[5]).astype(np.int)
  urcol = np.ceil((corners[0,3] - gt[0])/gt[1]).astype(np.int)
  urrow = np.floor((corners[1,3] - gt[3])/gt[5]).astype(np.int)

  return [ulcol, ulrow, (urcol-ulcol+1), (lrrow-ulrow+1)]
  
def ReprojectCoords(coords,src_srs,tgt_srs):
  ''' Reproject a list of x,y coordinates.

      @type geom:     C{tuple/list}
      @param geom:    List of [[x,y],...[x,y]] coordinates
      @type src_srs:  C{osr.SpatialReference}
      @param src_srs: OSR SpatialReference object
      @type tgt_srs:  C{osr.SpatialReference}
      @param tgt_srs: OSR SpatialReference object
      @rtype:         C{tuple/list}
      @return:        List of transformed [[x,y],...[x,y]] coordinates
  '''
  trans_coords=[]
  transform = osr.CoordinateTransformation( src_srs, tgt_srs)
  for x,y in coords:
    x,y,z = transform.TransformPoint(x,y)
    trans_coords.append([x,y])
  return trans_coords

## raster=r'somerasterfile.tif'
## ds=gdal.Open(raster)
## 
## gt=ds.GetGeoTransform()
## cols = ds.RasterXSize
## rows = ds.RasterYSize
## ext=GetExtent(gt,cols,rows)
## 
## src_srs=osr.SpatialReference()
## src_srs.ImportFromWkt(ds.GetProjection())
#tgt_srs=osr.SpatialReference()
#tgt_srs.ImportFromEPSG(4326)
## tgt_srs = src_srs.CloneGeogCS()
## 
## geo_ext=ReprojectCoords(ext,src_srs,tgt_srs)
