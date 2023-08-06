#!/usr/bin/env python2

'''Read and write image files as NumPy arrays
'''


from numpy import amax, amin, around, asarray, zeros as _zeros
from numpy import float32, uint8
from os.path import exists, splitext
from PIL import Image
from random import randint
from sys import float_info as _float_info


DEFAULT_DTYPE = float32


def channels(img):
    '''The number of 2D channels in a 3D array.
    '''
    _channels = lambda x, y, z=1: z
    return _channels(*img.shape)


def _normalize(array):
    '''Normalize an array to the interval [0,1].
    '''
    min = amin(array)
    max = amax(array)
    array -= min
    array /= max - min
    eps = 10.0 * _float_info.epsilon
    negs = array < 0.0 + eps
    array[negs] = 0.0
    bigs = array > 1.0 - eps
    array[bigs] = 1.0
    return


def read(filename, dtype=None):
    '''Return an array representing an image file.
    '''
    if dtype is None:
        dtype = DEFAULT_DTYPE
    img = Image.open(filename)
    arr = asarray(img, dtype=dtype)
    return arr


def _pil_save(img, filename):
    pil_img = Image.fromarray(img)
    pil_img.save(filename)
    return


def save(img, filename):
    '''Save an array as a unique image file and return its path.
    '''
    while True:
        newfile = splitext(filename)[0] + '-'
        newfile = newfile + str(randint(0, 1000)) + '.png'
        if not exists(newfile):
            break
    _normalize(img)
    uint8img = _zeros(img.shape, dtype=uint8)
    around(img * 255, out=uint8img)
    _pil_save(uint8img, newfile)
    return newfile


if __name__ == '__main__':
    pass
