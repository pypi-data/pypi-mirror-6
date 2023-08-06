#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    :synopsis: Detect caps from an image

    Description.
"""


# python 2.x support
from __future__ import division, print_function, absolute_import, unicode_literals

# standard modules
import sys

# 3rd party modules
import simplejson as json

# original modules
from capmoe.cv.capdetector import capdetector


def argparse():
    if len(sys.argv) != 3:
        print('Usage:  %s /path/to/image MAX_DETECT_NUM' % (sys.argv[0]),
              file=sys.stderr)
        sys.exit(1)
    imgpath, max_caididates = (sys.argv[1], int(sys.argv[2]))
    return (imgpath, max_caididates)


def main():
    imgpath, max_caididates = argparse()
    cap_circles = capdetector(imgpath, max_caididates)
    print(json.dumps(cap_circles))


if __name__ == '__main__':
    main()
