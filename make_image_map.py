import gdal
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib.pyplot as plt

indir = '/Volumes/DGE/CAO/caodata/Scratch/dknapp/Kaneohe/Reef_Mosaics/'
outfile = 'test_image_map.pdf'
inimage01 = 'patch13_20170905_test3_chla'
inimage02 = 'patch13_20170905_test3_chlc2'
inimage03 = 'patch25_20170905_test3_chla'
inimage04 = 'patch25_20170905_test3_chlc2'
inimage05 = 'patch42_20170905_test3_chla'
inimage06 = 'patch42_20170905_test3_chlc2'
inimage07 = 'patch44_20170905_test3_chla'
inimage08 = 'patch44_20170905_test3_chlc2'
inimage09 = 'patch4and5_20170905_test3_chla'
inimage10 = 'patch4and5_20170905_test3_chlc2'
inimage11 = 'patchHIMB_20170905_test3_chla'
inimage12 = 'patchHIMB_20170905_test3_chlc2'

with PdfPages('Kaneohe_ChlA_ChlC2.pdf') as pdf:
  ## Page 1
  inDS = gdal.Open(indir+inimage01)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  fig = plt.figure(figsize=(8,10))
  ax = plt.subplot(2, 1, 1)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=9.0, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  ax.set_title('Reef 13 Chl A (2017-09-05)')
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)

  inDS = gdal.Open(indir+inimage02)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  ax = plt.subplot(2, 1, 2)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=2.5, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  ax.set_title('Reef 13 Chl C2 (2017-09-05)')
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)
  pdf.savefig(fig)

  ## Page 2
  inDS = gdal.Open(indir+inimage03)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  fig = plt.figure(figsize=(8,10))
  ax = plt.subplot(2, 1, 1)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=10.0, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  ax.set_title('Reef 25 Chl A (2017-09-05)')
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)

  inDS = gdal.Open(indir+inimage04)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  ax = plt.subplot(2, 1, 2)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=3.0, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  ax.set_title('Reef 25 Chl C2 (2017-09-05)')
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)
  pdf.savefig(fig)

  ## Page 3
  inDS = gdal.Open(indir+inimage05)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  fig = plt.figure(figsize=(8,10))
  ax = plt.subplot(2, 1, 1)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=10.0, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  ax.set_title('Reef 42 Chl A (2017-09-05)')
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)

  inDS = gdal.Open(indir+inimage06)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  ax = plt.subplot(2, 1, 2)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=3.0, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  ax.set_title('Reef 42 Chl C2 (2017-09-05)')
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)
  pdf.savefig(fig)

  ## Page 4
  inDS = gdal.Open(indir+inimage07)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  fig = plt.figure(figsize=(8,10))
  ax = plt.subplot(2, 1, 1)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=9.0, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  ax.set_title('Reef 44 Chl A (2017-09-05)')
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)

  inDS = gdal.Open(indir+inimage08)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  ax = plt.subplot(2, 1, 2)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=2.5, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  ax.set_title('Reef 44 Chl C2 (2017-09-05)')
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)
  pdf.savefig(fig)

  ## Page 5
  inDS = gdal.Open(indir+inimage09)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  fig = plt.figure(figsize=(8,10))
  ax = plt.subplot(2, 1, 1)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=10.0, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  ax.set_title('Reef 4 and 5 Chl A (2017-09-05)')
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)

  inDS = gdal.Open(indir+inimage10)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  ax = plt.subplot(2, 1, 2)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=3.0, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  ax.set_title('Reef 4 and 5 Chl C2 (2017-09-05)')
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)
  pdf.savefig(fig)

  plt.close()

  ## Page 6
  inDS = gdal.Open(indir+inimage11)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  fig = plt.figure(figsize=(8,10))
  ax = plt.subplot(2, 1, 1)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=9.0, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  ax.set_title('Reef HIMB Chl A (2017-09-05)')
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)

  inDS = gdal.Open(indir+inimage12)
  band = inDS.GetRasterBand(1)
  ncols = inDS.RasterXSize
  nrows = inDS.RasterYSize
  data = band.ReadAsArray(0,0,ncols,nrows)

  ax = plt.subplot(2, 1, 2)
  im = ax.imshow(data, cmap='jet', vmin=0.0, vmax=2.5, interpolation='none')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
  ax.set_title('Reef HIMB Chl C2 (2017-09-05)')
  scalebar = ScaleBar(4.0, fixed_value=1000)
  fig.gca().add_artist(scalebar)
  cb = fig.colorbar(im, ax=ax)
  cb.set_label('g/cm2', rotation=0)
  pdf.savefig(fig)

  plt.close()
