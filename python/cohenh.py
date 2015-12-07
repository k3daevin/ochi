#!/usr/bin/env python

'''
Coherence-enhancing filtering example
=====================================

inspired by
  Joachim Weickert "Coherence-Enhancing Shock Filters"
  http://www.mia.uni-saarland.de/Publications/weickert-dagm03.pdf
'''

import numpy as np
import cv2


def coherence_filter(img, sigma = 11, str_sigma = 11, blend = 0.5, iter_n = 4, mctype=1):
    def make_gvv(channel):
        eigen = cv2.cornerEigenValsAndVecs(channel, str_sigma, -1)
        eigen = eigen.reshape(h, w, 3, 2)  # [[e1, e2], v1, v2]
        x, y = eigen[:,:,1,0], eigen[:,:,1,1]

        gxx = cv2.Sobel(channel, cv2.CV_32F, 2, 0, ksize=sigma)
        gxy = cv2.Sobel(channel, cv2.CV_32F, 1, 1, ksize=sigma)
        gyy = cv2.Sobel(channel, cv2.CV_32F, 0, 2, ksize=sigma)
        gvv = x*x*gxx + 2*x*y*gxy + y*y*gyy
        return gvv

    h, w = img.shape[:2]
    for i in xrange(iter_n):
        print i,

        if mctype == 0:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gvv = make_gvv(gray)
        elif mctype == 2:
            gvv_i = [make_gvv(img[:,:,i]) for i in xrange(3)]
            gvv = sum(gvv_i)
        elif mctype == 1:
            wi = [None] * 3
            for i in range(3):
                channel = img[:,:,i]
                eigen = cv2.cornerEigenValsAndVecs(channel, str_sigma, -1)
                eigen = eigen.reshape(h, w, 3, 2)  # [[e1, e2], v1, v2]
                x, y = eigen[:,:,1,0], eigen[:,:,1,1]
                wi[i] = (x, y)
            x = sum(w[0] for w in wi)
            y = sum(w[1] for w in wi)

            gi = [None] * 3
            for i in range(3):
                channel = img[:,:,i]
                gxx = cv2.Sobel(channel, cv2.CV_32F, 2, 0, ksize=sigma)
                gxy = cv2.Sobel(channel, cv2.CV_32F, 1, 1, ksize=sigma)
                gyy = cv2.Sobel(channel, cv2.CV_32F, 0, 2, ksize=sigma)
                gi[i] = (gxx, gxy, gyy)
            gxx = sum(g[0] for g in gi)
            gxy = sum(g[1] for g in gi)
            gyy = sum(g[2] for g in gi)

            gvv = x*x*gxx + 2*x*y*gxy + y*y*gyy

        m = gvv < 0

        ero = cv2.erode(img, None)
        dil = cv2.dilate(img, None)
        img1 = ero
        img1[m] = dil[m]
        img = np.uint8(img*(1.0 - blend) + img1*blend)
    print 'done'
    return img


if __name__ == '__main__':
    import sys
    try: fn = sys.argv[1]
    #except: fn = 'kev_horn.jpg'
    except: fn = 'julia.jpg'

    src = cv2.imread(fn)

    def nothing(*argv):
        pass

    def update():
        sigma = cv2.getTrackbarPos('sigma', 'coherence')*2+1
        str_sigma = cv2.getTrackbarPos('str_sigma', 'coherence')*2+1
        blend = cv2.getTrackbarPos('blend', 'coherence') / 10.0
        iter_n = cv2.getTrackbarPos('iter_n', 'coherence')
        print 'sigma: %d  str_sigma: %d  blend_coef: %f' % (sigma, str_sigma, blend)
        dst = coherence_filter(src, sigma=sigma, str_sigma = str_sigma, blend = blend, iter_n = iter_n)
        cv2.imwrite(fn + 'out.jpg', dst)
        cv2.imshow('dst', dst)
        return dst

    cv2.namedWindow('coherence', 0)
    cv2.createTrackbar('sigma', 'coherence', 9, 15, nothing)
    cv2.createTrackbar('blend', 'coherence', 7, 10, nothing)
    cv2.createTrackbar('str_sigma', 'coherence', 9, 15, nothing)
    cv2.createTrackbar('iter_n', 'coherence', 4, 20, nothing)
    

    print 'Press SPACE to update the image\n'

    cv2.imshow('src', src)
    dst = update()
    while True:
        ch = 0xFF & cv2.waitKey()
        if ch == ord(' '):
            dst = update()
        if ch == 27:
            break
    cv2.destroyAllWindows()