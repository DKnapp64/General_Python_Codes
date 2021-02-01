#!/Volumes/DGE/CAO/caodata/Code/optmemex/bin/python

import warnings
import pickle

with warnings.catch_warnings(record=True) as w:
  # Cause all warnings to be ignored.
  warnings.simplefilter("ignore")
  import spectral.io.envi as envi

from sklearn.ensemble import RandomForestClassifier
import numpy as np
import gdal
from gdalconst import *

cloudshadowlib01 = envi.open('cloud_shadow_speclib01.hdr')
cloudshadowlib02 = envi.open('cloud_shadow_speclib02.hdr')
cloudshadowlib03 = envi.open('cloud_shadow_speclib03.hdr')
cloudshadowlib04 = envi.open('cloud_shadow_speclib04.hdr')
cloudshadowlib05 = envi.open('cloud_shadow_speclib05.hdr')
cloudshadowlib06 = envi.open('cloud_shadow_speclib06.hdr')
cloudshadowlib07 = envi.open('cloud_shadow_speclib07.hdr')
cloudshadowlib08 = envi.open('cloud_shadow_speclib08.hdr')
cloudshadowlib09 = envi.open('cloud_shadow_speclib09.hdr')
cloudshadowlib10 = envi.open('cloud_shadow_speclib10.hdr')
cloudshadowlib11 = envi.open('cloud_shadow_speclib11.hdr')
cloudshadowlib12 = envi.open('cloud_shadow_speclib12.hdr')
cloudshadowlib13 = envi.open('cloud_shadow_speclib13.hdr')
cloudlib01 = envi.open('cloud_speclib01.hdr')
cloudlib02 = envi.open('cloud_speclib02.hdr')
cloudlib03 = envi.open('cloud_speclib03.hdr')
cloudlib04 = envi.open('cloud_speclib04.hdr')
cloudlib05 = envi.open('cloud_speclib05.hdr')
cloudlib06 = envi.open('cloud_speclib06.hdr')
cloudlib07 = envi.open('cloud_speclib07.hdr')
cloudlib08 = envi.open('cloud_speclib08.hdr')
cloudlib09 = envi.open('cloud_speclib09.hdr')
cloudlib10 = envi.open('cloud_speclib10.hdr')
cloudlib11 = envi.open('cloud_speclib11.hdr')
cloudlib12 = envi.open('cloud_speclib12.hdr')
cloudlib13 = envi.open('cloud_speclib13.hdr')
sunlitsurfacelib01 = envi.open('sunlit_surface_speclib01.hdr')
sunlitsurfacelib02 = envi.open('sunlit_surface_speclib02.hdr')
sunlitsurfacelib03 = envi.open('sunlit_surface_speclib03.hdr')
sunlitsurfacelib04 = envi.open('sunlit_surface_speclib04.hdr')

cloudshadow = np.concatenate((cloudshadowlib01.spectra, cloudshadowlib02.spectra, cloudshadowlib03.spectra,
                        cloudshadowlib04.spectra, cloudshadowlib05.spectra, cloudshadowlib06.spectra,
                        cloudshadowlib07.spectra, cloudshadowlib08.spectra, cloudshadowlib09.spectra,
                        cloudshadowlib10.spectra, cloudshadowlib11.spectra, cloudshadowlib12.spectra,
                        cloudshadowlib13.spectra), axis=0)
                        
cloud = np.concatenate((cloudlib01.spectra, cloudlib02.spectra, cloudlib03.spectra,
                  cloudlib04.spectra, cloudlib05.spectra, cloudlib06.spectra,
                  cloudlib07.spectra, cloudlib08.spectra, cloudlib09.spectra,
                  cloudlib10.spectra, cloudlib11.spectra, cloudlib12.spectra,
                  cloudlib13.spectra), axis=0)
surface = np.concatenate((sunlitsurfacelib01.spectra, sunlitsurfacelib02.spectra, sunlitsurfacelib03.spectra,
                  sunlitsurfacelib04.spectra), axis=0)

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

output = open('cloud_rf_hawaii_model.pkl', 'wb')
pickle.dump(clf, output)
output.close()


