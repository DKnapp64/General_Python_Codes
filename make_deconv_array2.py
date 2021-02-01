import numpy as np
from scipy.stats import norm

nr = 11
nc = 11
nb = 52

## 4 Targets + Sand
##  1000m AGL
## width = 2.9908
## alpha=0.277
## beta = 0.8695
## 4 Targets + Sand
##  500m AGL
## width = 5.5945
## alpha=0.1993
## beta = 0.8823

## Honaunau (6.5m pixels)
width = 5.0
alpha=0.1993
beta = 0.8823

Hr = np.zeros((nr,nr))
for i in range(nr):
  Hr[i,:] = norm.pdf(range(nr), i, width)
  Hr[i,:] = np.divide(Hr[i,:], np.sum(Hr[i,:]))

Hc = np.zeros((nc,nc))
for i in range(nc):
  Hc[i,:] = norm.pdf(range(nc), i, width)
  Hc[i,:] = np.divide(Hc[i,:], np.sum(Hc[i,:]))

Hri = np.linalg.pinv(beta * np.eye(nr) + (alpha * Hr))
Hci = np.linalg.pinv(beta * np.eye(nc) + (alpha * Hc))

##kernel = np.multiply(Hri, np.rot90(Hci))

## re-standardize
## sum of elements should equal 1.0
totalaround = np.sum(kernel)
