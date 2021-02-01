import os, sys
import gdal, osr
import glob
import subprocess

listrb = glob.glob('*_SR_rb.tif')

for rbfile in listrb:
  try:
    cmd = ['gdal_translate','-of','GTiff','-b','1','-b','2','-b','3']
    outfile = os.path.splitext(os.path.basename(rbfile))[0] + '_moorea.tif'
    cmd.extend(['-projwin','187200.0','8067600.0','211200.0','8050200.0'])
    cmd.extend(['-a_nodata','-9999.0'])
            for o in ogropts:
                if o.find(" ") > -1:
                    cmd.extend(o.split())
                else:
                    cmd.append(o)
            cmd.extend([outname,shp])
            for o in lcopts:
                cmd.extend(['-lco',o])
            sys.stdout.write("{}\n".format(" ".join(cmd)))
            if not echoonly:
                subprocess.check_call(cmd)
        except Exception as exc:
            sys.stderr.write('{}: Exception raised when combining file {}: {}\n'.format(name,shp,exc))
            sys.exit(1)

Usage: gdal_translate [--help-general] [--long-usage]
       [-ot {Byte/Int16/UInt16/UInt32/Int32/Float32/Float64/
             CInt16/CInt32/CFloat32/CFloat64}] [-strict]
       [-of format] [-b band] [-mask band] [-expand {gray|rgb|rgba}]
       [-outsize xsize[%]|0 ysize[%]|0] [-tr xres yres]
       [-r {nearest,bilinear,cubic,cubicspline,lanczos,average,mode}]
       [-unscale] [-scale[_bn] [src_min src_max [dst_min dst_max]]]* [-exponent[_bn] exp_val]*
       [-srcwin xoff yoff xsize ysize] [-epo] [-eco]
       [-projwin ulx uly lrx lry] [-projwin_srs srs_def]
       [-a_srs srs_def] [-a_ullr ulx uly lrx lry] [-a_nodata value]
       [-a_scale value] [-a_offset value]
       [-gcp pixel line easting northing [elevation]]*
       |-colorinterp{_bn} {red|green|blue|alpha|gray|undefined}]
       |-colorinterp {red|green|blue|alpha|gray|undefined},...]
       [-mo "META-TAG=VALUE"]* [-q] [-sds]
       [-co "NAME=VALUE"]* [-stats] [-norat]
       [-oo NAME=VALUE]*
       src_dataset dst_dataset

