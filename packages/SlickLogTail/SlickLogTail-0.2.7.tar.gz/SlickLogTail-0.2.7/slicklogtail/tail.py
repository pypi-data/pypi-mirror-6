from __future__ import print_function
# Copyright (c) 2013. SlickLog.
__author__ = 'Torindo Nesci'

from time import sleep
import os
import sys
from slicklog.remotelogger import ConnectionBuilder
from slicklog.remotelogger import SlickLogRemoteLogger
from slicklog.util import log

__TOOL_NAME = 'SlickLogTail'
__MIN_WAIT = 0.01
__MAX_WAIT = 5
__READ_SIZE = 1024


def _wait(interval):
  log('Sleeping {0}secs.', interval)
  sleep(interval)
  interval *= 2
  if interval > __MAX_WAIT:
    interval = __MAX_WAIT
  return interval


def _open_if_log_rotated(file, pos, size):
  wait_interval = __MIN_WAIT
  while True:
    try:
      return _try_reopen_if_rotated(file, pos, size)
    except Exception as ex:
      log('An exception occurred while opening rotated log: {0}.', str(ex))
      wait_interval = _wait(wait_interval)


def _try_reopen_if_rotated(file, pos, size):
  log('Trying to reopen {0}.', file.name)
  new_size = os.stat(file.name).st_size
  if new_size >= size:
    log('File not rotated.')
    return file, pos, size
  log('size={0}, new_size={1}.', size, new_size)
  log('File rotated. reopening.')
  try:
    file.close()
  except Exception as ex:
    log('An exception occurred while trying to close the file: {0}.', str(ex))

  new_file = open(file.name, 'rb')
  return new_file, 0, 0


def log_tail(filename):
  size = os.stat(filename).st_size
  log('{0}, size: {1}', filename, size)

  file = open(filename, 'rb')
  file.seek(size)
  wait_interval = __MIN_WAIT
  while True:
    pos = file.tell()
    bytes = file.read(__READ_SIZE)
    if bytes is None or len(bytes) == 0:
      log('no new data.')
      wait_interval = _wait(wait_interval)
      if wait_interval == __MAX_WAIT:
        file, pos, size = _open_if_log_rotated(file, pos, size)
      file.seek(pos)
    else:
      str = bytes.decode(sys.getdefaultencoding())
      log('Read {0}', str)
      yield str
      size += len(bytes)
      wait_interval = __MIN_WAIT


def _build_remote_logger(api_key, log_group_name, log_name, endpoint=None):
  conn_builder = ConnectionBuilder(api_key, log_group_name, log_name, endpoint)
  return SlickLogRemoteLogger(conn_builder, spawn_new_threads=False, daemon_thread=True)


def _slicklog_tail(remote_logger, logfile, suppress_print):
  for message in log_tail(logfile):
    if not suppress_print:
      print(message, end="")
    remote_logger.log(message)


def slicklog_tail(logfile, api_key, log_group_name, log_name, endpoint, suppress_print):
  print(' -- Running on Configuration --')
  print('  {0} => {1}'.format('logfile', logfile))
  print('  {0} => {1}'.format('log_group_name', log_group_name))
  print('  {0} => {1}'.format('log_name', log_name))

  wait_interval = __MIN_WAIT
  remote_logger = _build_remote_logger(api_key, log_group_name, log_name, endpoint)
  while True:
    try:
      _slicklog_tail(remote_logger, logfile, suppress_print)
    except Exception as ex:
      log('An error occurred while running {0}: {1}', __TOOL_NAME, str(ex))
      wait_interval = _wait(wait_interval)
