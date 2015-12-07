# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 06:14:32 2015

@author: testuser
"""

import scipy.cluster.vq as vq
from scipy import misc
import scipy.ndimage as nd
import numpy as np
import itertools
import sys
import time

def gencode(image, k, oldcenters=None):
  t1 = time.time()
  npix = image.size / 3
  P = np.reshape(image, (npix, 3), order='F')
  Pw = vq.whiten(P)
  if oldcenters == None:  
    (centers, label) = vq.kmeans2(Pw, k, iter=30)
  else:
    (centers, label) = vq.kmeans2(Pw, oldcenters, iter=5)
  (code, distortion) = vq.vq(Pw, centers)
  code = np.reshape(code, image.shape[0:2], order='F')
  print time.time() - t1
  return code, centers

def blur(image, k=1):
  return nd.filters.gaussian_filter(image, k)


def randomcolor(k):
  return np.array([np.random.uniform(0, 256, 3) for x in xrange(k)], dtype=np.uint8)

def rastacolor(k):
  x =  np.array([[0, 0 , 0], [255, 0, 0], [0, 255, 0], [255, 255, 0], [255, 255, 255], [0, 0, 255], [255, 0, 255], [0, 255, 255]], dtype=np.uint8)
  x = x[:k]
  if k > x.shape[0]:
    x = np.vstack((x, randomcolor(k - x.shape[0])))
  return x
  


if __name__ == "__main__":
  if len(sys.argv) == 1:
    imgfile = 'kev_horn.jpg'
  else:
    imgfile = sys.argv[1]
  ext = imgfile[-4:]
  imginput = misc.imread(imgfile)

  oldcenters = None
  image = imginput
#  for bidx, s in enumerate([0.0, 0.5, 0.75, 1, 1.25, 1.5, 2]):
#    print bidx
#    image = blur(imginput, s)
  code, oldcenters = gencode(image, 4, oldcenters)
  colors = rastacolor(False)

  for idx, c in enumerate(itertools.permutations(colors)):
    omage = np.array(c)[code]
    misc.imsave('out/' + imgfile + '_' + str(idx) + ext, omage)
      
      #break

  