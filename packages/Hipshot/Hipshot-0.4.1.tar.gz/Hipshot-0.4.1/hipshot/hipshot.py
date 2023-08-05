#!/usr/bin/env python2

'''Hipshot converts a video file into a single image
simulating a long-exposure photograph.
'''

import cv

from . import cvutils


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2013, 2014, Mansour Moufid'
__license__ = 'ISC'
__version__ = '0.4.1'
__email__ = 'mansourmoufid@gmail.com'
__status__ = 'Development'


def merge(frames, alpha, display=None):
    '''Average a list of frames with a weight factor of alpha,
    and optionally display the process in an OpenCV NamedWindow.
    '''
    acc = None
    for frame in frames:
        if not acc:
            acc = cvutils._template_image(frame, cv.IPL_DEPTH_32F)
        cv.RunningAvg(frame, acc, alpha)
        if display:
            cv.ShowImage(display, acc)
            k = cv.WaitKey(1)
            k = k & 255
            if k == ord('q'):
                break
            elif k == ord('z'):
                cv.SetZero(acc)
            elif k == ord('s'):
                print cvutils._save_image(acc, file, random=True)
    return acc


if __name__ == '__main__':
    pass
