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
    algorun = f[group]['algorithmrun_flag']
    l2aqual = f[group]['l2a_quality_flag']
    l2bqual = f[group]['l2b_quality_flag']
    degrade = f[group]['geolocation']['degrade_flag']
    surface_flag = f[group]['surface_flag']
    ## other data
    elev_high = f[group]['geolocation']['elev_highestreturn']
    elev_low = f[group]['geolocation']['elev_lowestmode']
    elev_bin0 = f[group]['geolocation']['elevation_bin0']
    elev_bin0_error = f[group]['geolocation']['elevation_bin0_error']
    elev_last = f[group]['geolocation']['elevation_lastbin']
    elev_last_error = f[group]['geolocation']['elevation_lastbin_error']
    hgt_bin0 = f[group]['geolocation']['height_bin0']
    hgt_lastbin = f[group]['geolocation']['height_lastbin']
    pgap_theta = f[group]['pgap_theta']
    pgap_theta_error = f[group]['pgap_theta_error']
    rh100 = f[group]['rh100']
    beam = f[group]['beam']
    lons = f[group]['geolocation']['longitude_bin0']
    lats = f[group]['geolocation']['latitude_bin0']
    shotnum = f[group]['geolocation']['shot_number']
    sensi = f[group]['sensitivity']
    solarelev = f[group]['geolocation']['solar_elevation']
    cover = f[group]['cover']
    landsattreecov = f[group]['land_cover_data']['landsat_treecover']
    modistreecov = f[group]['land_cover_data']['modis_treecover']
    pai = f[group]['pai']
    inside = np.zeros((pai.shape[0]), dtype=np.bool)
    ## good = np.all(goodstack, axis=0)
    for j in range(pai.shape[0]):
      if (pec_env.geometry[0].contains(Point(lons[j], lats[j])) \
        and (algorun[j] > 0) and (l2aqual[j] > 0) and (l2bqual[j] > 0) \
        and (solarelev[j] < 0.0)):
        inside[j] = True
    if (np.sum(inside) == 0):
      print("Shapefile for %s with %d surviving shots" % (group, np.sum(inside)))
      continue
    algorun = algorun[inside]
    l2aqual = l2aqual[inside]
    l2bqual = l2bqual[inside]
    degrade = degrade[inside]
    surface_flag = surface_flag[inside]
    elev_high = elev_high[inside]
    elev_low = elev_low[inside]
    elev_last = elev_last[inside]
    elev_last_error = elev_last_error[inside]
    elev_bin0 = elev_bin0[inside]
    elev_bin0_error = elev_bin0_error[inside]
    hgt_bin0 = hgt_bin0[inside]
    hgt_lastbin = hgt_lastbin[inside]
    beam = beam[inside]
    lons = lons[inside]
    lats = lats[inside]
    shotnum = shotnum[inside]
    cover = cover[inside]
    landsattreecov = landsattreecov[inside]
    modistreecov = modistreecov[inside]
    sensi = sensi[inside]
    solarelev = solarelev[inside]
    pai = pai[inside]
    pgap_theta = pgap_theta[inside]
    pgap_theta_error = pgap_theta_error[inside]
    rh100 = rh100[inside]
    df['beam'] = beam
    ## put them in the data frame
    df['shot_number'] = shotnum
    df['elev_high'] = elev_high
    df['elev_low'] = elev_low
    df['height'] = elev_high - elev_low
    df['elev_last'] = elev_last
    df['elev_last_error'] = elev_last_error
    df['elev_bin0'] = elev_bin0
    df['elev_bin0_error'] = elev_bin0_error
    df['height2'] = elev_bin0 - elev_last
    df['hgt_bin0'] = hgt_bin0
    df['hgt_lastbin'] = hgt_lastbin
    df['height3'] = hgt_bin0 - hgt_lastbin
    df['cover'] = cover
    df['pai'] = pai
    df['pgap_theta'] = pgap_theta 
    df['pgap_theta_error'] = pgap_theta_error 
    df['rh100'] = rh100/100.0 
    df['lstreecov'] = landsattreecov
    df['modtreecov'] = modistreecov
    df['l2a_qual'] = l2aqual
    df['l2b_qual'] = l2bqual
    df['degrade'] = degrade
    df['sensi'] = sensi
    df['solarelev'] = solarelev
    df['algorun'] = algorun
    df.astype({'beam':'int32', 'shot_number':'uint64', 'elev_high':'float32', 'elev_low':'float32', \
      'height':'float32', 'elev_last':'float32', 'elev_last_error':'float32', 'elev_bin0':'float32',\
      'elev_bin0_error':'float32', 'height2':'float32', 'hgt_bin0':'float32', \
      'hgt_lastbin':'float32', 'height3':'float32', 'cover':'float32', 'pai':'float32', \
      'pgap_theta':'float32', 'pgap_theta_error':'float32', \
      'rh100':'float32', 'lstreecov':'float32', \
      'modtreecov':'float32', 'l2a_qual':'uint8', 'l2b_qual':'uint8', 'degrade':'uint8', \
      'sensi':'float32', 'solarelev':'float32', 'algorun':'uint8'}) 
    geometries = gpd.points_from_xy(lons, lats)
    gdf = gpd.GeoDataFrame(df, geometry=geometries)
    gdf.crs = '+init=epsg:4326' # WGS84
    gdf.to_file(os.path.splitext(fname)[0]+'_PEC_'+group+'.shp')
    print("Finished Shapefile for %s with %d shots" % (group, np.sum(inside)))

f.close()

