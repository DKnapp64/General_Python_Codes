#!/bin/env python3
import sys
import os
from planet import api
from planet.api import downloader
import gdal, ogr, osr
import utm
import copy
import csv

def download_planet(ullatlon, lrlatlon, outputdir):
  client = api.ClientV1()

  aoi = {
    "type": "Polygon",
    "coordinates": [
      [
        [float(ullatlon[0]), float(ullatlon[1])],
        [float(lrlatlon[0]), float(ullatlon[1])],
        [float(lrlatlon[0]), float(lrlatlon[1])],
        [float(ullatlon[0]), float(lrlatlon[1])],
        [float(ullatlon[0]), float(ullatlon[1])],
      ]
    ]
  }

  query = api.filters.and_filter(api.filters.geom_filter(aoi), \
    api.filters.range_filter('cloud_cover', lt=0.1), \
    api.filters.date_range('acquired', gt='2016-08-01', lt='2016-09-30'))

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

