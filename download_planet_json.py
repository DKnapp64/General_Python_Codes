#!/bin/env python3
import sys
import os
from planet import api
from planet.api import downloader
import gdal, ogr, osr
import json
import utm
import copy
import csv

def main(jsonfile, startdate, enddate, outputdir):
  client = api.ClientV1()

  with open(jsonfile, 'r') as f:
    data = json.load(f)
 
  aoi = data['features'][0]['geometry']
  ## aoi = {
  ##   "type": "Polygon",
  ##   "coordinates": [
  ##     [
  ##       [float(ullatlon[0]), float(ullatlon[1])],
  ##       [float(lrlatlon[0]), float(ullatlon[1])],
  ##       [float(lrlatlon[0]), float(lrlatlon[1])],
  ##       [float(ullatlon[0]), float(lrlatlon[1])],
  ##       [float(ullatlon[0]), float(ullatlon[1])],
  ##     ]
  ##   ]
  ## }

  query = api.filters.and_filter(api.filters.geom_filter(aoi), \
    api.filters.range_filter('cloud_cover', lt=0.1), \
    api.filters.date_range('acquired', gt=startdate, lt=enddate))

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
  mydownloader.download(results.items_iter(len(myreps)), ['analytic_sr'], outputdir)
  mydownloader.shutdown()
  print(('Finished with Download.'))
  return( 0 )

if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print("[ USAGE ] you must supply one argument: download_planet_json.py JSONfile outputdir")
    print("     JSONfile: A GEoJSON File with the area of interest identified")
    print("     startdate: a test string like this example 2019-01-01 for Jan 1, 2019")
    print("     enddate: a test string like this example 2019-03-01 for March 1, 2019")
    print("     outputdir: The output directory")
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )
