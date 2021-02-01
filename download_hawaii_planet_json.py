#!/bin/env python3
import sys
import os
from planet import api
from planet.api import downloader
import json
import numpy as np
import utm

def main(jsonfile, startdate, enddate, outputdir):
  PLANET_API_KEY = os.getenv('PL_API_KEY')

  client = api.ClientV1()

  with open(jsonfile, 'r') as f:
    data = json.load(f)
 
  aoi = data['features'][0]['geometry']

  query = api.filters.and_filter(api.filters.geom_filter(aoi), \
    api.filters.date_range('acquired', gt=startdate, lt=enddate))
    ## api.filters.range_filter('cloud_cover', gte=0.1), \

  item_types4 = ['PSScene4Band']
  request4 = api.filters.build_search_request(query, item_types4)
  item_types3 = ['PSScene3Band']
  request3 = api.filters.build_search_request(query, item_types3)

  results3 = client.quick_search(request3)
  results4 = client.quick_search(request4)

  myreps3 = []
  myreps4 = []
  list3 = []
  list4 = []
  
  for item in results4.items_iter(limit=100):
    list4.append(item)
    myreps4.append(item['id'])
    if (item['properties']['instrument'] == 'PS2.SD'):
      print(r'%s : %s' % (item['id'], 'Super Dove'))
    else:
      print(r'%s : %s' % (item['id'], 'Dove'))

  for item in results3.items_iter(limit=100):
    ## print(r'%s' % item['id'])
    myreps3.append(item['id'])

  if (len(myreps3) > len(myreps4)):
    diff34 = np.setdiff1d(myreps3, myreps4).tolist()                              
    print("\nPossible 3Band data that could be made to 4Band:")                     
    [ print("%s" % thisid) for thisid in diff34 ]
  
  print("\n")                     

  mydownloader = downloader.create(client)

  print((r'Starting Download of %d images.') % len(myreps4))
  mydownloader.download(results4.items_iter(limit=100), ['udm2'], outputdir)
  print(('Finished with Download of udm2.'))
  mydownloader.download(results4.items_iter(limit=100), ['analytic_sr'], outputdir)
  print(('Finished with Download of analytic_sr.'))
  mydownloader.download(results4.items_iter(limit=100), ['analytic_xml'], outputdir)
  print(('Finished with Download of metadata_xml.'))
  mydownloader.shutdown()
  print(('Downloader has been shut down.'))
  return( 0 )

if __name__ == "__main__":

  if len( sys.argv ) != 5:
    print("[ USAGE ] you must supply 4 arguments: download_hawaii_planet_json.py JSONfile startdate enddate outputdir")
    print("     JSONfile: A GEoJSON File with the area of interest identified")
    print("     startdate: a test string like this example 2019-01-01 for Jan 1, 2019")
    print("     enddate: a test string like this example 2019-03-01 for March 1, 2019")
    print("     outputdir: The output directory")
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )
