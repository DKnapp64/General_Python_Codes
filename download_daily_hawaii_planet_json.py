#!/bin/env python3
import sys
import os
from planet import api
from planet.api import downloader
import json
import numpy as np
from datetime import datetime, timedelta, timezone, tzinfo
import pdb

def main(jsonfile, outputdir):
  PLANET_API_KEY = os.getenv('PL_API_KEY')

  root = os.path.basename(outputdir)
  if (root == ''):
    root = os.path.split(os.path.split(outputdir)[0])[1]
  today = datetime.today()
  ## today = datetime.today() - timedelta(days=1)
  logfilename = "download_log_"+("%s_%04d%02d%02d.txt" % (root, today.year, today.month, today.day))
  f = open(logfilename, 'w+')

  settime1 = datetime(today.year, today.month, today.day, 23, 0, 0, 0, timezone.utc)
  back1 = timedelta(days=3)
  yesterday = settime1 - back1
  timetxt1 = yesterday.isoformat(timespec='minutes')[0:16]
  timetxt2 = settime1.isoformat(timespec='minutes')[0:16]

  f.write('Searching for files between %s and %s\n' % (timetxt1, timetxt2))

  client = api.ClientV1()

  ## jsonfile1 = '/scratch/dknapp4/Western_Hawaii/NW_Big_Island_Intensive_Study_Area.json'
  ## jsonfile2 = '/scratch/dknapp4/Western_Hawaii/SW_Big_Island_Intensive_Study_Area.json'

  with open(jsonfile, 'r') as f2:
    data = json.load(f2)
 
  aoi = data['features'][0]['geometry']

  query = api.filters.and_filter(api.filters.geom_filter(aoi), \
    api.filters.date_range('acquired', gt=timetxt1, lt=timetxt2))
    ## api.filters.range_filter('cloud_cover', lt=0.1), \

  item_types4 = ['PSScene4Band']
  request4 = api.filters.build_search_request(query, item_types4)
  item_types3 = ['PSScene3Band']
  request3 = api.filters.build_search_request(query, item_types3)

  results3 = client.quick_search(request3)
  results4 = client.quick_search(request4)
  pdb.set_trace()

  myreps3 = []
  myreps4 = []
  list3 = []
  list4 = []
  
  for item in results4.items_iter(limit=100):
    list4.append(item)
    myreps4.append(item['id'])
    if (item['properties']['instrument'] == 'PS2.SD'):
      f.write(('%s : %s\n') % (item['id'], 'Dove-R'))
    else:
      f.write(('%s : %s\n') % (item['id'], 'Dove-Classic'))

  for item in results3.items_iter(limit=100):
    ## print(r'%s' % item['id'])
    myreps3.append(item['id'])

  if (len(myreps3) > len(myreps4)):
    diff34 = np.setdiff1d(myreps3, myreps4).tolist()                              
    f.write("\nPossible 3Band data that could be made to 4Band:")                     
    ## [ f.write("%s\n" % thisid) for thisid in diff34 ]
    for thisid in diff34:
      f.write("%s\n" % thisid)
  
  f.write("\n")

  ## urlform = 'https://api.planet.com/data/v1/item-types/{}/items/{}/assets'
  ## for myid in myreps4:
  ##   theassets = client.get_assets(myid).get()
  ##   if ('analytic_sr' in theassets):
  ##     activation = client.activate(assets['analytic_sr'])
  ##     ## wait for activation
  ##     theassets = client.get_assets(myid).get()
  ##     callback = api.write_to_file(directory=outputdir, callback=None, overwrite=True)
  ##     body = client.download(assets['analytic_sr'], callback=callback)
  ##     body.await()
  ## resget = requests.get(urlform.format('analytic_sr', myid), auth=HTTPBasicAuth(PLANET_API_KEY, '')) 
    
  mydownloader = downloader.create(client, no_sleep=True, astage__size=10, 
    pstage__size=10, pstage__min_poll_interval=0, dstage__size=2)

  ## put the results into a regular list
  ## mylist = []
  ## for item in list4:
  ##   item 
  ##  whole[1]['properties']['instrument'] == 'PS2.SD'

  f.write(('Starting Download of %d scenes.\n') % len(myreps4))
  mydownloader.download(results4.items_iter(limit=100), ['udm2'], outputdir)
  f.write(('Finished with Download of udm2.\n'))
  mydownloader.download(results4.items_iter(limit=100), ['analytic_sr'], outputdir)
  f.write(('Finished with Download of analytic_sr.\n'))
  mydownloader.download(results4.items_iter(limit=100), ['analytic_xml'], outputdir)
  f.write(('Finished with Download of analytic_xml.\n'))
  mydownloader.shutdown()
  f.write(('Downloader has been shut down.\n'))
  f.close()
  return( 0 )

if __name__ == "__main__":

  if len( sys.argv ) != 3:
    print("[ USAGE ] you must supply 2 arguments: download_daily_hawaii_planet_json.py jsonfile outputdir")
    print("     jsonfile: JSON file indicating area to download image for")
    print("     outputdir: The output directory")
    sys.exit( 0 )

  main( sys.argv[1], sys.argv[2] )
