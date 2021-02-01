import numpy as np
import gdal, ogr, osr
import sys

infile = '/lustre/scratch/cao/dknapp/Hawaii17CORAL/ortho/hawaii_vswir_coral_honaunaumerc_20170623_mosaic_negdepth_surface'
outfile = '/lustre/scratch/cao/dknapp/Hawaii17CORAL/ortho/hawaii_vswir_coral_honaunaumerc_20170623_mosaic_negdepth_surface2'

fillvalue = 19.80
ds = gdal.Open(infile)

## get data type
datatype = ds.GetRasterBand(1).DataType

# Create for target raster the same projection as for the value raster
raster_srs = osr.SpatialReference()
raster_srs.ImportFromWkt(ds.GetProjectionRef())

outXsize = ds.RasterXSize + 10
outYsize = ds.RasterYSize + 10

driver = ds.GetDriver()
outDs = driver.Create(outfile, outXsize, outYsize, ds.RasterCount, datatype) 

## create geotransform of mosaic bounds
gt = ds.GetGeoTransform()
newgt = tuple((gt[0] - (5 * gt[1]), gt[1], np.double(0.0), gt[3] - (5 * gt[5]), np.double(0.0), gt[5]))
outDs.SetGeoTransform(newgt)

outDs.SetProjection(raster_srs.ExportToWkt())

full = np.zeros((outYsize, outXsize, ds.RasterCount), dtype=np.float32) + fillvalue

for band in range(ds.RasterCount):
  data = ds.GetRasterBand(band+1)
  full[5:(5+ds.RasterYSize), 5:(5+ds.RasterXSize), 0] = data.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize)

outBand = outDs.GetRasterBand(1)
outBand.WriteArray(full[:,:,0])
outBand.FlushCache()
outBand.SetNoDataValue(0)

del ds, outDs
