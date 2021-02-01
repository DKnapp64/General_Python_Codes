import numpy as np
from scipy.stats import norm

nr = 11
nc = 11

## 500m AGL
width = 5.5954
alpha = 0.1993
beta = 0.8823

## 1000m AGL
width = 2.9908
alpha = 0.277
beta = 0.8695

Hr = np.zeros((nr,nr))
for i in range(nr):
  Hr[i,:] = norm.pdf(range(nr), i, 5)
  Hr[i,:] = np.divide(Hr[i,:], np.sum(Hr[i,:]))

Hc = np.zeros((nc,nc))
for i in range(nc):
  Hc[i,:] = norm.pdf(range(nc), i, 5)
  Hc[i,:] = np.divide(Hc[i,:], np.sum(Hc[i,:]))

Hri = np.linalg.pinv(beta * np.eye(nr) + (alpha * Hr))
Hci = np.linalg.pinv(beta * np.eye(nc) + (alpha * Hc))


