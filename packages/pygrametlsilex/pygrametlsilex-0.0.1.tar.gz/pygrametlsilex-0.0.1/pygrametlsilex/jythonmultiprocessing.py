# -*- coding: utf-8 -*-
""" A module for Jython emulating (a small part of) CPython's multiprocessing.
    With this, pygrametl can be made to use multiprocessing, but actually use       threads when used from Jython (where there is no GIL).
"""

__author__ = "Christian Thomsen"
__maintainer__ = "Sílex Sistemas Ltda."
__version__ = '0.0.1'
__all__ = ['JoinableQueue', 'Process', 'Queue', 'Value']

import sys
if not sys.platform.startswith('java'):
    raise ImportError, 'jythonmultiprocessing is made for Jython'

from threading import Thread
from Queue import Queue
from pygrametl.jythonsupport import Value


class Process(Thread):
    pid = '<n/a>'
    daemon = property(Thread.isDaemon, Thread.setDaemon)
    name = property(Thread.getName, Thread.setName)


class JoinableQueue(Queue):
    def close(self):
        pass