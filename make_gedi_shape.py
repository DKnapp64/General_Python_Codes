#!/usr/bin/env python3
import h5py
import pandas as pd
import numpy as np
import geopandas as gpd
import os, sys
import time

fname = sys.argv[1]
f = h5py.File(fname, 'r')
print(list(f.keys()))

groups = [t for t in f.keys()]

print("File: %s" % (fname))

for group in groups:
    if (group == 'METADATA'):
        continue

    latitude_bin0 = f[group]['geolocation']['latitude_bin0']
    longitude_bin0 = f[group]['geolocation']['longitude_bin0']
    ## isqual = np.logical_and(np.equal(l2a_quality_flag, 1), np.equal(l2b_quality_flag, 1))
    valid_x = np.isfinite(longitude_bin0)
    valid_y = np.isfinite(latitude_bin0)
    within_x = np.logical_and(np.greater(longitude_bin0,-76.04), np.less(longitude_bin0,-74.93))
    within_y = np.logical_and(np.greater(latitude_bin0,-7.5), np.less(latitude_bin0,-7.29))
    goodstack = np.stack((valid_x, valid_y, within_x, within_y))
    good = np.all(goodstack, axis=0)
    if (np.sum(good) == 0):
        print("No valid values in group %s" % (group))
        time.sleep(5)
        continue

    ##  Geolocation GROUP
    shot_number = f[group]['geolocation']['shot_number']
    degrade_flag = f[group]['geolocation']['degrade_flag']
    delta_time = f[group]['geolocation']['delta_time']
    digital_elevation_model = f[group]['geolocation']['digital_elevation_model']
    elev_highestreturn = f[group]['geolocation']['elev_highestreturn']
    elev_lowestmode = f[group]['geolocation']['elev_lowestmode']
    elevation_bin0 = f[group]['geolocation']['elevation_bin0']
    elevation_bin0_error = f[group]['geolocation']['elevation_bin0_error']
    elevation_lastbin = f[group]['geolocation']['elevation_lastbin']
    elevation_lastbin_error = f[group]['geolocation']['elevation_lastbin_error']
    height_bin0 = f[group]['geolocation']['height_bin0']
    height_lastbin = f[group]['geolocation']['height_lastbin']
    lat_highestreturn = f[group]['geolocation']['lat_highestreturn']
    lat_lowestmode = f[group]['geolocation']['lat_lowestmode']
    latitude_bin0_error = f[group]['geolocation']['latitude_bin0_error']
    latitude_lastbin = f[group]['geolocation']['latitude_lastbin']
    latitude_lastbin_error = f[group]['geolocation']['latitude_lastbin_error']
    local_beam_azimuth = f[group]['geolocation']['local_beam_azimuth']
    local_beam_elevation = f[group]['geolocation']['local_beam_elevation']
    lon_highestreturn = f[group]['geolocation']['lon_highestreturn']
    lon_lowestmode = f[group]['geolocation']['lon_lowestmode']
    longitude_bin0_error = f[group]['geolocation']['longitude_bin0_error']
    longitude_lastbin = f[group]['geolocation']['longitude_lastbin']
    longitude_lastbin_error = f[group]['geolocation']['longitude_lastbin_error']
    solar_azimuth = f[group]['geolocation']['solar_azimuth']
    solar_elevation = f[group]['geolocation']['solar_elevation']
    ##  No GROUP
    l2a_quality_flag = f[group]['l2a_quality_flag']
    l2b_quality_flag = f[group]['l2b_quality_flag']
    ##  Land Cover Data GROUP
    landsat_treecover = f[group]['land_cover_data']['landsat_treecover']
    modis_nonvegetated = f[group]['land_cover_data']['modis_nonvegetated']
    modis_nonvegetated_sd = f[group]['land_cover_data']['modis_nonvegetated_sd']
    modis_treecover = f[group]['land_cover_data']['modis_treecover']
    modis_treecover_sd = f[group]['land_cover_data']['modis_treecover_sd']
    ##  No GROUP
    master_frac = f[group]['master_frac']
    master_int = f[group]['master_int']
    num_detectedmodes = f[group]['num_detectedmodes']
    omega = f[group]['omega']
    pai = f[group]['pai']
    ## pai_z = f[group]['pai_z']
    ## pavd_z = f[group]['pavd_z']
    pgap_theta = f[group]['pgap_theta']
    pgap_theta_error = f[group]['pgap_theta_error']
    ## pgap_theta_z = f[group]['pgap_theta_z']
    rg = f[group]['rg']
    rh100 = f[group]['rh100']
    rhog = f[group]['rhog']
    rhog_error = f[group]['rhog_error']
    rhov = f[group]['rhov']
    rhov_error = f[group]['rhov_error']
    rossg = f[group]['rossg']
    rv = f[group]['rv']
    rhog = f[group]['rhog']
    ##  SKIPPING THE RX_PROCESSING GROUP
    ##  No GROUP
    rx_range_highestreturn = f[group]['rx_range_highestreturn']
    rx_sample_count = f[group]['rx_sample_count']
    rx_sample_start_index = f[group]['rx_sample_start_index']
    selected_l2a_algorithm = f[group]['selected_l2a_algorithm']
    selected_rg_algorithm = f[group]['selected_rg_algorithm']
    sensitivity = f[group]['sensitivity']
    stale_return_flag = f[group]['stale_return_flag']
    surface_flag = f[group]['surface_flag']

    ## Create dataframe and load the good values
    df = pd.DataFrame()
 
    df['shot_number'] = shot_number[good]
    df['degrade_flag'] = degrade_flag[good]
    df['delta_time'] = delta_time[good]
    df['digital_elevation_model'] = digital_elevation_model[good]
    df['elev_highestreturn'] = elev_highestreturn[good]
    df['elev_lowestmode'] = elev_lowestmode[good]
    df['elevation_bin0'] = elevation_bin0[good]
    df['elevation_bin0_error'] = elevation_bin0_error[good]
    df['elevation_lastbin'] = elevation_lastbin[good]
    df['elevation_lastbin_error'] = elevation_lastbin_error[good]
    df['height_bin0'] = height_bin0[good]
    df['height_lastbin'] = height_lastbin[good]
    df['lat_highestreturn'] = lat_highestreturn[good]
    df['lat_lowestmode'] = lat_lowestmode[good]
    df['latitude_bin0'] = latitude_bin0[good]
    df['latitude_bin0_error'] = latitude_bin0_error[good]
    df['latitude_lastbin'] = latitude_lastbin[good]
    df['latitude_lastbin_error'] = latitude_lastbin_error[good]
    df['local_beam_azimuth'] = local_beam_azimuth[good]
    df['local_beam_elevation'] = local_beam_elevation[good]
    df['lon_highestreturn'] = lon_highestreturn[good]
    df['lon_lowestmode'] = lon_lowestmode[good]
    df['longitude_bin0'] = longitude_bin0[good]
    df['longitude_bin0_error'] = longitude_bin0_error[good]
    df['longitude_lastbin'] = longitude_lastbin[good]
    df['longitude_lastbin_error'] = longitude_lastbin_error[good]
    df['solar_azimuth'] = solar_azimuth[good]
    df['solar_elevation'] = solar_elevation[good]
    df['l2a_quality_flag'] = l2a_quality_flag[good]
    df['l2b_quality_flag'] = l2b_quality_flag[good]
    df['landsat_treecover'] = landsat_treecover[good]
    df['modis_nonvegetated'] = modis_nonvegetated[good]
    df['modis_nonvegetated_sd'] = modis_nonvegetated_sd[good]
    df['modis_treecover'] = modis_treecover[good]
    df['modis_treecover_sd'] = modis_treecover_sd[good]
    df['master_frac'] = master_frac[good]
    df['master_int'] = master_int[good]
    df['num_detectedmodes'] = num_detectedmodes[good]
    df['omega'] = omega[good]
    df['pai'] = pai[good]
    ## pdb.set_trace()
    ## df['pai_z'] = pai_z[good]
    ## df['pavd_z'] = pavd_z[good]
    df['pgap_theta'] = pgap_theta[good]
    df['pgap_theta_error'] = pgap_theta_error[good]
    ## df['pgap_theta_z'] = pgap_theta_z[good]
    df['rg'] = rg[good]
    df['rh100'] = rh100[good]
    df['rhog'] = rhog[good]
    df['rhog_error'] = rhog_error[good]
    df['rhov'] = rhov[good]
    df['rhov_error'] = rhov_error[good]
    df['rossg'] = rossg[good]
    df['rv'] = rv[good]
    df['rhog'] = rhog[good]
    df['rx_range_highestreturn'] = rx_range_highestreturn[good]
    df['rx_sample_count'] = rx_sample_count[good]
    df['rx_sample_start_index'] = rx_sample_start_index[good]
    df['selected_l2a_algorithm'] = selected_l2a_algorithm[good]
    df['selected_rg_algorithm'] = selected_rg_algorithm[good]
    df['sensitivity'] = sensitivity[good]
    df['stale_return_flag'] = stale_return_flag[good]
    df['surface_flag'] = surface_flag[good]
    geometries = gpd.points_from_xy(longitude_bin0[good], latitude_bin0[good])
    gdf = gpd.GeoDataFrame(df, geometry=geometries)
    gdf.crs = '+init=epsg:4326' # WGS84
    outfile = 'Shapes/' + os.path.basename(fname)+'_PEC_'+group+'.shp'
    gdf.to_file(outfile+'_PEC_'+group+'.shp')
    print("Finished Shapefile for %s with %d shots" % (group, np.sum(good)))
    
f.close()

