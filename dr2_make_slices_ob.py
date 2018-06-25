import numpy
from scipy.ndimage.filters import gaussian_filter as gf
from scipy.special import expit, logit
import sys
import os
import matplotlib.pyplot as plt
import imageio.core
import cv2
from math import sqrt

#config

rootDir = 'd:/projects/astronomy/gaia_dr2/'

#code

number_of_bins = 3
w = 3000//number_of_bins
z_height = 600//number_of_bins
sigma = 15//number_of_bins
spread = 300
ciLimit = 0.0 #OB
magLimit = 7

poeLimit = 10

count = 0

#a = numpy.zeros(shape=(w*2,w*2,340),dtype='float32')

a = numpy.memmap(rootDir+'output/huge_file.dat',mode='w+',shape=(2*w,2*w,2*z_height),dtype='float32')

fp = open(rootDir+'output/star_list/all_stars_0.1.csv','r')
line = fp.readline()
while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        name, colourIndex, xg, yg, zg, glon, glat, m, plx,plx_over_err,extinction,excess,nonNullCut,flagCut,dataCut = bits
        name_stripped = name.split(' ')[2]
        poe = float(plx_over_err)
        absMag = float(m)
        ci = float(colourIndex)

        if (poe > poeLimit) and (flagCut == '1') and (dataCut == '1') and (absMag < magLimit) and (ci < ciLimit):
            x = float(xg)/number_of_bins
            y = float(yg)/number_of_bins
            if sqrt(x*x+y*y) < w :
                x = int(round(float(xg)/number_of_bins))+w
                y = int(round(float(yg)/number_of_bins))+w
                z = int(round(float(zg)/number_of_bins))+z_height
                if (x >= 0) and (x < 2*w) and (y >= 0) and (y < 2*w) and (z >= 0) and (z < 2*z_height):
                    a[x][y][z] += 1
                    count += 1
    line = fp.readline()
fp.close()

gaussian = gf(a, sigma=sigma, truncate=3)
b = 2*(expit(spread*gaussian)-0.5)

if not os.path.isdir(rootDir+'output/slices'):
    os.mkdir(rootDir+'output/slices')

sliceDir = rootDir+'output/slices/hot/'

if not os.path.isdir(sliceDir):
    os.mkdir(sliceDir)

if not os.path.isdir(sliceDir+'cm'):
    os.mkdir(sliceDir+'cm')

if not os.path.isdir(sliceDir+'16bit'):
    os.mkdir(sliceDir+'16bit')

#for dr2Slice in numpy.dsplit(b,2*w):
for sliceCount in range(0,2*z_height):
    dr2Slice = b[:,:,sliceCount]
    print('slice', sliceCount)

    filename=sliceDir+'16bit/slice_'+str(sliceCount).zfill(4)+'.pgm'
    b2 = imageio.core.image_as_uint(dr2Slice, bitdepth=16)
    cv2.imwrite(filename,b2)

    filename=sliceDir+'cm/slice_'+str(sliceCount).zfill(4)+'.png'
    plt.imsave(filename,dr2Slice.squeeze(),cmap='inferno')

print(count,'stars')
for i in range(1,100):
    y = i/100
    x = logit((y+1)/2)/spread
    print(y,x)
