#!/bin/env python2
import numpy as np
import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import sys

vswirfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/patch44_for_histo_rb_4cm'
dicamfile = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/Reef_44_for_histo_dimac_4cm'
pdffile = 'dimac_histograms.pdf'

########################################################
# Open data
## red = 45
## green = 27
## blue = 9

vswir = gdal.Open(vswirfile)
dicam = gdal.Open(dicamfile)

xoff = 0
yoff = 0
xcountvswir = vswir.RasterXSize
ycountvswir = vswir.RasterYSize
xcountdicam = dicam.RasterXSize
ycountdicam = dicam.RasterYSize

bandvswirRed = vswir.GetRasterBand(45).ReadAsArray()
bandvswirGreen = vswir.GetRasterBand(27).ReadAsArray()
bandvswirBlue = vswir.GetRasterBand(9).ReadAsArray()

nodatared = vswir.GetRasterBand(45).GetNoDataValue()
nodatagreen = vswir.GetRasterBand(27).GetNoDataValue()
nodatablue = vswir.GetRasterBand(9).GetNoDataValue()

goodred = np.not_equal(np.float32(bandvswirRed.flatten()), np.float32(nodatared))
goodgreen = np.not_equal(np.float32(bandvswirGreen.flatten()), np.float32(nodatagreen))
goodblue = np.not_equal(np.float32(bandvswirBlue.flatten()), np.float32(nodatablue))

vswirRed = np.float32(bandvswirRed.flatten())[goodred]
vswirGreen = np.float32(bandvswirGreen.flatten())[goodgreen]
vswirBlue = np.float32(bandvswirBlue.flatten())[goodblue]

banddicamRed = dicam.GetRasterBand(1).ReadAsArray()
banddicamGreen = dicam.GetRasterBand(2).ReadAsArray()
banddicamBlue = dicam.GetRasterBand(3).ReadAsArray()

hist, bins = np.histogram(banddicamRed.flatten(), bins=50)
center = (bins[:-1] + bins[1:])/2
width = 0.7 * (bins[1] - bins[0])
plt.bar(center, hist, align='center', width=width)

with PdfPages('patch44_vswir_dimac_histograms.pdf') as pdf:
  ## Page 1, Red
  fig = plt.figure(figsize=(8,10))

  ax = plt.subplot(2, 1, 1)
  ax.set_title('Reef 44 VSWIR Red Histogram')

  percent1 = np.percentile(vswirRed, 1)
  percent99 = np.percentile(vswirRed, 99)
  hist, bins = np.histogram(vswirRed, bins=50, range=(percent1, percent99))
  center = (bins[:-1] + bins[1:])/2
  width = 0.7 * (bins[1] - bins[0])
  plt.bar(center, hist, align='center', width=width)

  ax = plt.subplot(2, 1, 2)
  ax.set_title('Reef 44 DiMAC Red Histogram')

  percent1 = np.percentile(banddicamRed.flatten(), 1)
  percent99 = np.percentile(banddicamRed.flatten(), 99)
  hist, bins = np.histogram(banddicamRed.flatten(), bins=50, range=(percent1, percent99))
  center = (bins[:-1] + bins[1:])/2
  width = 0.7 * (bins[1] - bins[0])
  plt.bar(center, hist, align='center', width=width)

  pdf.savefig(fig)
  plt.close()

  ## Page 2, Green
  fig = plt.figure(figsize=(8,10))

  ax = plt.subplot(2, 1, 1)
  ax.set_title('Reef 44 VSWIR Green Histogram')

  percent1 = np.percentile(vswirGreen, 1)
  percent99 = np.percentile(vswirGreen, 99)
  hist, bins = np.histogram(vswirGreen, bins=50, range=(percent1, percent99))
  center = (bins[:-1] + bins[1:])/2
  width = 0.7 * (bins[1] - bins[0])
  plt.bar(center, hist, align='center', width=width)

  ax = plt.subplot(2, 1, 2)
  ax.set_title('Reef 44 DiMAC Green Histogram')

  percent1 = np.percentile(banddicamGreen.flatten(), 1)
  percent99 = np.percentile(banddicamGreen.flatten(), 99)
  hist, bins = np.histogram(banddicamGreen.flatten(), bins=50, range=(percent1, percent99))
  center = (bins[:-1] + bins[1:])/2
  width = 0.7 * (bins[1] - bins[0])
  plt.bar(center, hist, align='center', width=width)

  pdf.savefig(fig)
  plt.close()

  ## Page 3, Blue
  fig = plt.figure(figsize=(8,10))

  ax = plt.subplot(2, 1, 1)
  ax.set_title('Reef 44 VSWIR Blue Histogram')

  percent1 = np.percentile(vswirBlue, 1)
  percent99 = np.percentile(vswirBlue, 99)
  hist, bins = np.histogram(vswirBlue, bins=50, range=(percent1, percent99))
  center = (bins[:-1] + bins[1:])/2
  width = 0.7 * (bins[1] - bins[0])
  plt.bar(center, hist, align='center', width=width)

  ax = plt.subplot(2, 1, 2)
  ax.set_title('Reef 44 DiMAC Blue Histogram')

  percent1 = np.percentile(banddicamBlue.flatten(), 1)
  percent99 = np.percentile(banddicamBlue.flatten(), 99)
  hist, bins = np.histogram(banddicamBlue.flatten(), bins=50, range=(percent1, percent99))
  center = (bins[:-1] + bins[1:])/2
  width = 0.7 * (bins[1] - bins[0])
  plt.bar(center, hist, align='center', width=width)

  pdf.savefig(fig)
  plt.close()

  d = pdf.infodict()
  d['Title'] = 'Histograms of Reef 44 VSWIR and DiMAC images'
  d['Author'] = 'David Knapp'
  d['Subject'] = 'CAO Coral work'
  d['CreationDate'] = datetime.datetime(2018, 2, 1)
  d['ModDate'] = datetime.datetime.today()


del vswir, dicam
