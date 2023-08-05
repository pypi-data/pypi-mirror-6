#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTTP streaming toolbox with flow control, written in Python.

:copyright: (c) 2013 Runzhou Li (Leo)
:license: The MIT License (MIT), see LICENSE for details.
"""

__title__ = 'tidehunter'
__version__ = '0.1.9'
__author__ = 'Runzhou Li (Leo)'
__license__ = 'The MIT License (MIT)'
__copyright__ = 'Runzhou Li (Leo)'

from . import stream

# Set default logging handler to avoid "No handler found" warnings.
import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:  # pragma: no cover
    class NullHandler(logging.Handler):

        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
