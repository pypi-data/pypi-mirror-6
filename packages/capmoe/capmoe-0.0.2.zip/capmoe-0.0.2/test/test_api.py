# -*- coding: utf-8 -*-
"""
     :synopsis: Test CapMoe's API libraries

     Description.
 """


# python 2.x support
from __future__ import division, print_function, absolute_import, unicode_literals

# standard modules
from os.path import join, dirname

# 3rd party modules
from nose_parameterized import parameterized
import cv2

# original modules
from capmoe.cv.capdetector import capdetector


# constants
IMG_DIR = join(dirname(__file__), 'images')


def has_circle_nearly_eq(query_circle, target_circles, img_size):
    """Check if :param:`query_circle` is in :param:`target_circles`

    Minor error on center point and radius are allowed

    :type query_circle: (x, y, r)
    :type target_circles: (x, y, r), ...
    :param img_size: Size of image from which circles are detected.
        Used for calculating acceptable error.
    """
    err_px = int(min(img_size) * 0.1)

    def circle_nearly_eq(circle0, circle1):
        return (abs(circle0['x'] - circle1['x']) <= err_px and
                abs(circle0['y'] - circle1['y']) <= err_px and
                abs(circle0['r'] - circle1['r']) <= err_px)

    for target_circle in target_circles:
        if circle_nearly_eq(query_circle, target_circle):
            return True
    return False


@parameterized([
    # ('img_name', {'x': cap_x, 'y': cap_y, 'r': cap_r}) ; checked by my eyes!
    ('1a.jpg', {'x': 453, 'y': 273, 'r': 136}),
    ('1b.jpg', {'x': 255, 'y': 140, 'r': 67}),
    ('2b.jpg', {'x': 441, 'y': 325, 'r': 124}),
    ('3a.jpg', {'x': 437, 'y': 299, 'r': 144}),
    ('3b.jpg', {'x': 441, 'y': 310, 'r': 147}),
    ('4a.jpg', {'x': 386, 'y': 320, 'r': 116}),
    ('4b.jpg', {'x': 455, 'y': 310, 'r': 126}),
    ('5a.jpg', {'x': 432, 'y': 319, 'r': 126}),
    ('5b.jpg', {'x': 442, 'y': 289, 'r': 115}),
    ('5c.jpg', {'x': 860, 'y': 640, 'r': 250}),
])
def test_capdetector(img_name, cap_circle):
    """Test if capdetector detect a cap from an image correctly.

    If cap is detected in 5 candidates, it's OK.
    """
    img_path = join(IMG_DIR, img_name)
    im       = cv2.imread(img_path)
    img_size = im.shape[0:2]

    cap_candidates = capdetector(img_path, max_candidates=5)
    assert(has_circle_nearly_eq(cap_circle, cap_candidates, img_size))
