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
import subprocess

def download_planet(ullatlon, lrlatlon, outputdir):
  client = api.ClientV1()

  ## done = download_planet(ullatlon, lrlatlon, outputdir)

  aoi = {
    "type": "Polygon",
    "coordinates": [
      [
        [ullatlon[0], ullatlon[1]],
        [lrlatlon[0], ullatlon[1]],
        [lrlatlon[0], lrlatlon[1]],
        [ullatlon[0], lrlatlon[1]],
        [ullatlon[0], ullatlon[1]],
      ]
    ]
  }

  query = api.filters.and_filter(api.filters.geom_filter(aoi), \
    api.filters.range_filter('cloud_cover', lt=0.1), \
    api.filters.date_range('acquired', gt='2016-08-01', lt='2018-04-30'))

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


done = download_planet([-155.830,20.025],[-155.822,20.015], "/scratch/dknapp4/hawaii_invariant")
