import rasterio
import numpy

with rasterio.drivers():
  with rasterio.open('baikal_subset.tif') as src:
      b1, b2, b3, b4, b5 = src.read()

      profile = src.profile
      profile.update(
        dtype=rasterio.float64,
        count=1,
        compress='lzw')

  ndvi = numpy.zeros(b1.shape)
  ndvi = (b1-b2)/(b1+b2)

  with rasterio.open('ndvi_python.tif', 'w', **profile) as dst:
    dst.write(ndvi.astype(rasterio.float64), 1)
