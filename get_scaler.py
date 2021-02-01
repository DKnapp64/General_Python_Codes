#!/bin/env python3
import geojson
import os, sys

"""
Because the Heatmap intensities are all relative, we need a way to
scale the heatmap points each week.  This code is written to determine 
the scaling factor for the heatmap points based on the number of points.
The scaler is relative to the number of points in the first week of the
monitoring period.  It is used in the HTML file in which the MapBoxGL 
HeatMap is generated.
          // increase weight count increases
          'heatmap-weight': [
            'interpolate',
            ['exponential', 1.25],
            ['get', 'Count'],
            0,
            0,
            15 * USE_SCALER_HERE,
            1,
          ],
The arguments are the GeoJSON file of the first week of the monitoring
and the week for the new heatmap.  It returns the scale factor.
"""

def get_scaler(firstweek, thisweek):

    f = open(firstweek, 'r')
    stuff = geojson.load(f)
    f.close()
    numpts_week1 = len(stuff.features)
    del stuff

    f = open(thisweek, 'r')
    stuff = geojson.load(f)
    f.close()
    numpts_weekN = len(stuff.features)
    return 2 * (float(numpts_week1)/numpts_weekN)
