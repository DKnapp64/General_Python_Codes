#!/Volumes/DGE/CAO/caodata/Code/optmemex/bin/python

import warnings
import pickle

def fxn():
  warnings.warn("user", UserWarning)

with warnings.catch_warnings(record=True) as w:
  # Cause all warnings to be ignored.
  warnings.simplefilter("ignore")
  import spectral.io.envi as envi

from sklearn.ensemble import RandomForestClassifier
import numpy as np
import gdal
from gdalconst import *

cloudshadowlibcasi = envi.open('cloud_shadow_speclib_combined_casi.hdr')
cloudlibcasi = envi.open('cloud_speclib_combined_casi.hdr')
sunlitsurfacelibcasi = envi.open('sunlit_surface_speclib_combined_casi.hdr')

cloudshadow = cloudshadowlibcasi.spectra
cloud = cloudlibcasi.spectra
surface = sunlitsurfacelibcasi.spectra

cloudshadow.shape[0]
cloud.shape[0]
surface.shape[0]

X = np.concatenate((cloud, cloudshadow, surface), axis=0)
print X.shape

cloudlabels = np.ones(cloud.shape[0], dtype=np.int) * 63
cloudshadowlabels = np.ones(cloudshadow.shape[0], dtype=np.int) * 127
surfacelabels = np.ones(surface.shape[0], dtype=np.int) * 255
y = np.concatenate((cloudlabels, cloudshadowlabels, surfacelabels), axis=0)
print y.shape

clf = RandomForestClassifier(n_estimators=30, criterion="gini", max_features="auto", max_depth=None, n_jobs=-1, random_state=0)
rfmodel = clf.fit(X, y)

output = open('cloud_rf_hawaii_model_casi.pkl', 'wb')
pickle.dump(clf, output)
output.close()


