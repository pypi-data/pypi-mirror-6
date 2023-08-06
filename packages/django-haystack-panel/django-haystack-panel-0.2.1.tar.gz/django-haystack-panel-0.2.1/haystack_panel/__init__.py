# -*- coding: utf-8 -*-

"""
haystack_panel
~~~~~~~~~~~~~~

:copyright: (c) 2014 by Chris Streeter.
:license: See LICENSE for more details.

"""

import pkg_resources

try:
    __version__ = pkg_resources.get_distribution('haystack_panel').version
except Exception:
    __version__ = 'unknown'


__title__ = 'haystack_panel'
__author__ = 'Chris Streeter'
__copyright__ = 'Copyright 2014 Chris Streeter'

VERSION = __version__
