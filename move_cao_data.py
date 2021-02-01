import shutil, sys, os, os.path
import re

topdir = '/Volumes/DGE/CAO/caodata/Sites/Oahu/coral/2017_Sep/vswir/'

def uniquecao(top):
  directory = None
  listprefix = []

  ## Go through it to find all files beginning with "CAO"
  for root, dirs, files in os.walk(top):
    for name in files:
      if (name[0:3] == 'CAO'):
        listprefix.append(name[0:18])

  ## Create set of unique prefixes
  listpreunique = list(set(listprefix))

  ## for dirit in listpreunique:
  ##   os.mkdir(top+dirit, 0775)
