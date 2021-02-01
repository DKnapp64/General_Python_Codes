#!/usr/bin/python
## import gdal, ogr, osr, numpy
import sys

import spectral
import spectral.io.envi as envi

img = spectral.io.envi.open(in_hdr, in_file)

img = envi.open(in_hdr, in_file)
envi.read_subregion((0,1), (0,img.shape[1]), use_memmap=False)

inmm = img.open_memmap(interleave='source', writable=False)
wl = s.array([float(w) for w in img.metadata['wavelength']])
if (wl[0] < 100): 
wl = wl * 1000
fwhm = s.array([float(w) for w in img.metadata['fwhm']])

# set up metadata and constants
  const = constants(wl, args.mode, scenario, args.root_dir+'/data/')

  # make output Rb file and open memmap
  metadata = img.metadata.copy()
  metadata['bands'] = '%i' % sum(const.use_out)
  metadata['interleave'] = 'bil'
  metadata['wavelength'] = ['%7.2f'%w for w in wl[const.use_out]]
  metadata['data type'] = '2'
  out = envi.create_image(out_hdr, metadata, ext='',force=True)
  outmm = out.open_memmap(interleave='source', writable=True)


  for i in range(start, fin):

    # Flush cache 
    print 'line %i/%i' % (i,nl)

    if args.depth_file is not None:
      del bathy
      bathy= spectral.io.envi.open(args.depth_file+'.hdr', args.depth_file)
      bathymm = bathy.open_memmap(interleave='source', writable=False)
      bath = s.array(bathymm[i,:,:])
      if bathy.metadata['interleave'] == 'bil':
          bath = bath.T
    else:
      bath = None

########################################################
# Open data
raster = gdal.Open(input_value_raster)

# Create for target raster the same projection as for the value raster
raster_srs = osr.SpatialReference()
raster_srs.ImportFromWkt(raster.GetProjectionRef())
target_ds.SetProjection(raster_srs.ExportToWkt())

# Read raster as arrays
banddataraster = raster.GetRasterBand(1)
dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)


def main(input_zone_polygon, input_value_raster):
    return loop_zonal_stats(input_zone_polygon, input_value_raster)


if __name__ == "__main__":

    #
    # Returns for each feature a dictionary item (FID) with the statistical values in the following order: Average, Mean, Medain, Standard Deviation, Variance, NumberofElements
    #
    # example run : $ python grid.py <full-path><output-shapefile-name>.shp xmin xmax ymin ymax gridHeight gridWidth
    # example run : ~/python_stuff/get_raster_stats_under_shapes.py anp_nacional_05_08_2016.shp peru_100m_dem_tif.tif
    #

    if len( sys.argv ) != 3:
        print "[ ERROR ] you must supply two arguments: input-zone-shapefile-name.shp input-value-raster-name.tif "
        sys.exit( 1 )
    print 'Returns for each feature a dictionary item (FID) with the statistical values in the following order: Mean, Median, Standard Deviation, Variance, NumberofElements'
    print main( sys.argv[1], sys.argv[2] )
