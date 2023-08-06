# -*- coding: utf-8 -*-
"""
    capmoe.api
    ~~~~~~~~~~

    :synopsis: Python API, wrapper for `bin/capmoe-*` scripts

    Description.
"""


# python 2.x support
from __future__ import division, print_function, absolute_import, unicode_literals

# standard modules
import os
import shlex
from subprocess import Popen, PIPE

# 3rd party modules
import simplejson as json

# original modules


def _command_exec(cmd):
    p = Popen(shlex.split(cmd),
              stdin=None, stdout=PIPE, stderr=PIPE,
              env=os.environ)
    exitcode = p.wait()
    if exitcode != 0:
        raise OSError(
'''Command `%s` failed with exitcode %d.

Output from stderr:
%s''' % (cmd, exitcode, p.stderr.read()))

    return json.loads(p.stdout.read())


def capdetector(imgpath, max_candidates):
    cmd = 'capmoe-capdetector.py "%s" %d' % (imgpath, max_candidates)
    return _command_exec(cmd)
