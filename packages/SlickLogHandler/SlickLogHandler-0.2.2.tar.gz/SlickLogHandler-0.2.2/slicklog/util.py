# Copyright (c) 2013. SlickLog.
__author__ = 'Torindo Nesci'

import sys


__DEBUG_ENABLED = False


def log(message, *args):
  if __DEBUG_ENABLED:
    print(message.format(*args))


def set_debug(debug):
  global __DEBUG_ENABLED
  __DEBUG_ENABLED = debug


def is_debug_enabled():
  return __DEBUG_ENABLED


def quote_p(string):
  if py3():
    return _py3_quote_plus(string)
  return _py2_quote_plus(string)


def u(string):
  if py3():
    return str(string)
  return unicode(string)


def new_queue(max_size=None):
  if py3():
    return _py3_queue(max_size)
  return _py2_queue(max_size)


def queue_mod():
  if py3():
    return _py3_queue_mod()
  return _py2_queue_mod()


def httplib_mod():
  if py3():
    return _py3_httplib_mod()
  return _py2_httplib_mod()


def _py2_httplib_mod():
  import httplib
  return httplib


def _py3_httplib_mod():
  import http.client
  return http.client


def _py2_queue_mod():
  import Queue
  return Queue


def _py3_queue_mod():
  import queue
  return queue


def _py2_queue(max_size=None):
  from Queue import Queue
  return Queue(maxsize=max_size)


def _py3_queue(max_size=None):
  from queue import Queue
  return Queue(maxsize=max_size)


def _py2_quote_plus(string):
  from urllib import quote_plus
  return quote_plus(string)


def _py3_quote_plus(string):
  from urllib.parse import quote_plus
  return quote_plus(string)


def py3():
  return sys.version_info[0] >= 3




