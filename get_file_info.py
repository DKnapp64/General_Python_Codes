import os
import subprocess
import re
from os.path import join, getsize

rawdirs = ['California_Aug07', 'California_Jan12', 'California_Jul12'
    'California_Jul13', 'California_Jun11', 'California_May15', 
    'Chilliwack', 'Colombia_Feb12', 'Colombia_Jan11', 'Hawaii_Dec07', 
    'Hawaii_Feb07', 'Hawaii_Jan07', 'Hawaii_Jan08', 'Hawaii_Jan09', 
    'Hawaii_May07', 'Hawaii_Oct07', 'Hawaii_Sep07', 'Hawaii_Test_Nov06', 
    'Kruger_AprilMay12', 'Kruger_MarchApril08', 'Kruger_MarchApril10',
    'Panama_Feb11', 'Panama_Jan12', 'Panama_Oct09', 'Peru11', 'Madagascar_marchapril10', 
    'Peru12', 'Peru13', 'Peru_Aug09', 'SouthAfrica_2014', 'SouthAfrica_2015']

for j in range(len(rawdirs)):
  for root, dirs, files in os.walk('/caofs/Campaigns2/'+rawdirs[j]):
    for name in files:
      result = subprocess.Popen(["fsfileinfo", join(root, name)], stdout=subprocess.PIPE)
      out = result.stdout.read()
      print out

