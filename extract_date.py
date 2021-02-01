#!/bin/env python3
import os, sys

def extract_date(infile):
  parts = infile.split('_')
  middle = parts.index('to') 
  if (middle != -1):
    startit = parts[middle-1]
    endit = parts[middle+1]
    if ((len(startit)) == 8 and startit.isnumeric() and endit.isnumeric()):
      stdate = datetime.datetime(int(startit[0:4]), int(endit[4:6]), int(endit[6:]))
      enddate = datetime.datetime(int(endit[0:4]), int(endit[4:6]), int(endit[6:]))
    else if (len(startit) == 10):
      if startit[0:4].isnumeric: yr = startit[0:4]
      if startit[5:7].isnumeric: mon = startit[5:7]
      if startit[8:].isnumeric: day = startit[8:]
      stdate = datetime.datetime(int(yr), int(mon), int(day))
      if endit[0:4].isnumeric: yr = endit[0:4]
      if endit[5:7].isnumeric: mon = endit[5:7]
      if endit[8:].isnumeric: day = endit[8:]
      enddate = datetime.datetime(int(yr), int(mon), int(day))
    return((startdate, enddate))
  else:
    return((NULL, NULL))
