#!/usr/bin/env python3
import h5py
import pandas as pd
import numpy as np
from shapely.geometry import Point
import geopandas as gpd
import os, sys

fname = sys.argv[1]

f = h5py.File(fname, 'r')

## haydi_bre(f)
## print(list(f.keys()))

groups = [t for t in f.keys()]

print("File: %s" % (fname))

## read in GeoJSON of Peru, Ecuador, Colombia envelope
pec_env = gpd.read_file('pec_env2.geojson')

for group in groups:
    if (group == 'METADATA' or group == 'BEAM0000' or group == 'BEAM0001' \
      or group == 'BEAM0010' or group == 'BEAM0011'):
        continue
    df = pd.DataFrame()
    ## quality flags
    algocnt = f[group]['ancillary']['l2a_alg_count']
    algosel = f[group]['selected_algorithm']
    qual = f[group]['quality_flag']
    rh = f[group]['rh']
    degrade = f[group]['degrade_flag']
    ## other data
    hi_mode1 = f[group]['geolocation']['elevs_allmodes_a1']
    hi_mode2 = f[group]['geolocation']['elevs_allmodes_a2']
    hi_mode3 = f[group]['geolocation']['elevs_allmodes_a3']
    hi_mode4 = f[group]['geolocation']['elevs_allmodes_a4']
    hi_mode5 = f[group]['geolocation']['elevs_allmodes_a5']
    hi_mode6 = f[group]['geolocation']['elevs_allmodes_a6']
    lo_mode = f[group]['elev_lowestmode']
    beam = f[group]['beam']
    lons = f[group]['lon_lowestmode']
    lats = f[group]['lat_lowestmode']
    shotnum = f[group]['geolocation']['shot_number']
    sensi = f[group]['sensitivity']
    solarelev = f[group]['solar_elevation']
    landsattreecov = f[group]['land_cover_data']['landsat_treecover']
    modistreecov = f[group]['land_cover_data']['modis_treecover']
    dem = f[group]['digital_elevation_model']
    inside = np.zeros((algosel.shape[0]), dtype=np.bool)
    for j in range(algosel.shape[0]):
      if (pec_env.geometry[0].contains(Point(lons[j], lats[j])) \
        and (qual[j] > 0) and (solarelev[j] < 0.0)):
        inside[j] = True
    if (np.sum(inside) == 0):
      print("Shapefile for %s with %d surviving shots" % (group, np.sum(inside)))
      continue
    
    algosel = algosel[inside]
    qual = qual[inside]
    rh00 = rh[inside, 0]
    rh25 = rh[inside, 25]
    rh50 = rh[inside, 50]
    rh75 = rh[inside, 75]
    rh76 = rh[inside, 76]
    rh77 = rh[inside, 77]
    rh78 = rh[inside, 78]
    rh79 = rh[inside, 79]
    rh80 = rh[inside, 80]
    rh81 = rh[inside, 81]
    rh82 = rh[inside, 82]
    rh83 = rh[inside, 83]
    rh84 = rh[inside, 84]
    rh85 = rh[inside, 85]
    rh86 = rh[inside, 86]
    rh87 = rh[inside, 87]
    rh88 = rh[inside, 88]
    rh89 = rh[inside, 89]
    rh90 = rh[inside, 90]
    rh91 = rh[inside, 91]
    rh92 = rh[inside, 92]
    rh93 = rh[inside, 93]
    rh94 = rh[inside, 94]
    rh95 = rh[inside, 95]
    rh96 = rh[inside, 96]
    rh97 = rh[inside, 97]
    rh98 = rh[inside, 98]
    degrade = degrade[inside]
    hi_mode1 = hi_mode1[inside,0]
    hi_mode2 = hi_mode2[inside,0]
    hi_mode3 = hi_mode3[inside,0]
    hi_mode4 = hi_mode4[inside,0]
    hi_mode5 = hi_mode5[inside,0]
    hi_mode6 = hi_mode6[inside,0]
    lo_mode = lo_mode[inside]
    beam = beam[inside]
    lons = lons[inside]
    lats = lats[inside]
    shotnum = shotnum[inside]
    landsattreecov = landsattreecov[inside]
    modistreecov = modistreecov[inside]
    sensi = sensi[inside]
    solarelev = solarelev[inside]
    dem = dem[inside]
    ## put them in the data frame
    df['beam'] = beam
    df['shot_number'] = shotnum
    df['qual'] = qual
    df['rh00'] = rh00
    df['rh25'] = rh25
    df['rh50'] = rh50
    df['rh75'] = rh75
    df['rh76'] = rh76
    df['rh77'] = rh77
    df['rh78'] = rh78
    df['rh79'] = rh79
    df['rh80'] = rh80
    df['rh81'] = rh81
    df['rh82'] = rh82
    df['rh83'] = rh83
    df['rh84'] = rh84
    df['rh85'] = rh85
    df['rh86'] = rh86
    df['rh87'] = rh87
    df['rh88'] = rh88
    df['rh89'] = rh89
    df['rh90'] = rh90
    df['rh91'] = rh91
    df['rh92'] = rh92
    df['rh93'] = rh93
    df['rh94'] = rh94
    df['rh95'] = rh95
    df['rh96'] = rh96
    df['rh97'] = rh97
    df['rh98'] = rh98
    df['hi_mode1'] = hi_mode1
    df['hi_mode2'] = hi_mode2
    df['hi_mode3'] = hi_mode3
    df['hi_mode4'] = hi_mode4
    df['hi_mode5'] = hi_mode5
    df['hi_mode6'] = hi_mode6
    df['lo_mode'] = lo_mode
    df['hgt_mode1'] = hi_mode1 - lo_mode
    df['hgt_mode2'] = hi_mode2 - lo_mode
    df['hgt_mode3'] = hi_mode3 - lo_mode
    df['hgt_mode4'] = hi_mode4 - lo_mode
    df['hgt_mode5'] = hi_mode5 - lo_mode
    df['hgt_mode6'] = hi_mode6 - lo_mode
    df['lstreecov'] = landsattreecov
    df['modtreecov'] = modistreecov
    df['degrade'] = degrade
    df['sensi'] = sensi
    df['solarelev'] = solarelev
    df['algosel'] = algosel
    df['dem'] = dem
    df.astype({'beam':'int32', 'shot_number':'uint64', 'qual':'uint8', \
      'rh00':'float32', 'rh25':'float32', 'rh50':'float32', \
      'rh75':'float32', 'rh76':'float32', 'rh77':'float32', 'rh78':'float32', \
      'rh79':'float32', 'rh80':'float32', 'rh81':'float32', 'rh82':'float32', \
      'rh83':'float32', 'rh84':'float32', 'rh85':'float32', 'rh86':'float32', \
      'rh87':'float32', 'rh88':'float32', 'rh89':'float32', 'rh90':'float32', \
      'rh91':'float32', 'rh92':'float32', 'rh93':'float32', 'rh94':'float32', \
      'rh95':'float32', 'rh96':'float32', 'rh97':'float32', \
      'rh98':'float32', 'hi_mode1':'float32', 'hi_mode2':'float32', \
      'hi_mode3':'float32', 'hi_mode4':'float32', 'hi_mode5':'float32', \
      'hi_mode6':'float32', 'lo_mode':'float32', 'hgt_mode1':'float32', \
      'hgt_mode2':'float32', 'hgt_mode3':'float32', 'hgt_mode4':'float32', \
      'hgt_mode5':'float32', 'hgt_mode6':'float32', 'lstreecov':'float32', \
      'modtreecov':'float32', 'degrade':'uint8', 'sensi':'float32', \
      'solarelev':'float32', 'algosel':'uint8', 'dem':'float32'}) 
    geometries = gpd.points_from_xy(lons, lats)
    gdf = gpd.GeoDataFrame(df, geometry=geometries)
    gdf.crs = '+init=epsg:4326' # WGS84
    gdf.to_file(os.path.splitext(fname)[0]+'_PEC_'+group+'.shp')
    print("Finished Shapefile for %s with %d shots" % (group, np.sum(inside)))

f.close()

