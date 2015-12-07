# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 17:40:24 2015

@author: testuser
"""

import numpy as np
import cv2
import sys
from scipy import misc
import itertools
import cohenh
import colreduce
import time


if __name__ == "__main__":
  if len(sys.argv) == 1:
    imgfile = 'kev_horn.jpg'
    #imgfile = 'julia.png'
  else:
    imgfile = sys.argv[1]
  ext = imgfile[-4:]
  #imginput = misc.imread(imgfile)
  imginput = cv2.imread(imgfile)
  class CR:
    oldcenters = None
    k = 4
    colors = [np.array(x)[:,(2,1,0)] for x in itertools.permutations(colreduce.rastacolor(k))]
    code = None
    src = None
    coh = None
    dst = None
    def __init__(self, src):
      self.src = src
    def permcolor(self):
      self.colors = [np.array(x)[:,(2,1,0)] for x in itertools.permutations(colreduce.rastacolor(self.k))]
    def randcolor(self):
      self.colors = [np.array(x)[:,(2,1,0)] for x in itertools.permutations(colreduce.randomcolor(self.k))]
  
  
  cr = CR (imginput) 
  
  def nothing(*argv):
      pass

  def update_coh():
      sigma = cv2.getTrackbarPos('sigma', 'coherence')*2+1
      str_sigma = cv2.getTrackbarPos('str_sigma', 'coherence')*2+1
      blend = cv2.getTrackbarPos('blend', 'coherence') / 100.0
      iter_n = cv2.getTrackbarPos('iter_n', 'coherence')
      print 'sigma: %d  str_sigma: %d  blend_coef: %f' % (sigma, str_sigma, blend)
      cr.coh = cohenh.coherence_filter(cr.src, sigma=sigma, str_sigma = str_sigma, blend = blend, iter_n = iter_n)
      cv2.imshow('coh', cr.coh)
  
  def update_k(*argv):
      oldk = cr.k
      cr.k = cv2.getTrackbarPos('k', 'posterize')+2
      cr.permcolor()
      if True:#oldk != cr.k:
        destroy_posterize_window()
        cr.oldcenters = None
        update_cod()
        create_posterize_window()
      update_col()
      
  
  def update_cod():
      cr.code, cr.oldcenters = colreduce.gencode(cr.coh, cr.k, cr.oldcenters)
  
  def update_col(*argv):
      idx = cv2.getTrackbarPos('colorset', 'posterize')
      cr.dst = cr.colors[idx][cr.code]
      cv2.imshow('dst', cr.dst)
  
  cv2.namedWindow('coherence', 0)
  cv2.createTrackbar('sigma', 'coherence', 4, 15, nothing)
  cv2.createTrackbar('blend', 'coherence', 25, 100, nothing)
  cv2.createTrackbar('str_sigma', 'coherence', 5, 15, nothing)
  cv2.createTrackbar('iter_n', 'coherence', 50, 100, nothing)

  def create_posterize_window():
    cv2.namedWindow('posterize', 0)
    cv2.createTrackbar('k', 'posterize', cr.k-2, 6, nothing)
    cv2.createTrackbar('colorset', 'posterize', 0, len(cr.colors)-1, update_col)

  def destroy_posterize_window():
    cv2.destroyWindow('posterize')
  
  create_posterize_window()

  cv2.imshow('src', cr.src)
  update_coh()
  update_cod()
  update_col()
  while True:
    ch = 0xFF & cv2.waitKey()
    if ch == ord(' '):
      update_coh()
      update_cod()
      update_col()
    elif ch == ord('r'):
      cr.randcolor()
      update_col()
    elif ch == ord('a'):
      cr.permcolor()
      update_col()
    elif ch == ord('k'):
      update_k()
    elif ch == ord('s'):
      timestamp = str(time.time())
      cv2.imwrite(imgfile + timestamp + "_coh_" + ext, cr.coh)
      cv2.imwrite(imgfile + timestamp + "_dst_" + ext, cr.dst)
    elif ch == 27:
      break
  cv2.destroyAllWindows()
