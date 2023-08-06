from __future__ import print_function
from __future__ import division
# Copyright (c) 2013. SlickLog.
__author__ = 'Torindo Nesci'

import sys
from time import sleep
import errno
from os import stat
from os import listdir
from os.path import dirname
from os.path import join
from os.path import split
from os.path import basename
from os.path import isfile
from slicklog.remotelogger import ConnectionBuilder
from slicklog.remotelogger import SlickLogRemoteLogger
from slicklog.util import log
from slicklog.util import is_debug_enabled
from .fuzzy import levenshtein_distance
from .fuzzy import to_vect
from .fuzzy import cos_similarity

__TOOL_NAME = 'SlickLogTail'
__MIN_WAIT = 0.01
__MAX_WAIT = 5
__READ_SIZE = 1024
__FILE_SIMILARITY_TH = 0.95
__LEIV_DIST_TH = 0.50


def _files_in_dir(dir, exclude_files_set=None):
  if exclude_files_set is None:
    exclude_files_set = set()
  if dir is None or len(dir) == 0:
    dir = '.'
  log('listing files in dir:{0} with exlude files:{1}', dir, exclude_files_set)
  files = set()
  for f in listdir(dir):
    if isfile(join(dir, f)) and f not in exclude_files_set:
      files.add(f)
  if is_debug_enabled():
    for f in files:
      log(' file found in dir {0}: {1}', dir, f)
  return files


def _get_best_file_match(file, files):
  chars, mod = to_vect(file)
  min_dist = sys.maxint
  min_file = None
  for f in files:
    similarity = cos_similarity(chars, mod, f)
    log('Similarity between {0} and {1} is {2}.', file, f, similarity)
    if similarity > __FILE_SIMILARITY_TH:
      dist = levenshtein_distance(file, f)
      edit_perc = dist / len(file)
      log('Leiv distance between {0} and {1} is {2}, perc edit is {3}.', file, f, dist, edit_perc)
      if edit_perc < __LEIV_DIST_TH and dist < min_dist:
        min_dist = dist
        min_file = f
  return min_file


def _wait(interval):
  log('Sleeping {0}secs.', interval)
  sleep(interval)
  interval *= 2
  if interval > __MAX_WAIT:
    interval = __MAX_WAIT
  return interval


def _open_if_log_rotated(file, pos, size, old_files, fuzzy_rotation):
  wait_interval = __MIN_WAIT
  while True:
    try:
      try:
        new_file = _try_reopen_if_rotated(file, size)
        if new_file is not None:
          return new_file, 0, 0, _files_in_dir(dirname(file.name))
      except OSError as err:
        log('An error occurred while reopening log {0}: {1}.', file.name, repr(err))
        if err.errno != errno.ENOENT or not fuzzy_rotation:
          raise err
      if fuzzy_rotation:
        new_file = _try_reopen_if_fuzzy_rotated(file, old_files)
        if new_file is not None:
          return new_file, 0, 0, _files_in_dir(dirname(file.name))
      return file, pos, size, old_files
    except Exception as ex:
      log('An exception occurred while opening rotated log: {0}.', repr(ex))
      wait_interval = _wait(wait_interval)


def path_leaf(path):
    head, tail = split(path)
    return tail or basename(head)


def _try_reopen_if_fuzzy_rotated(file, old_files):
  dir = dirname(file.name)
  if dir is None or len(dir) == 0:
    dir = '.'
  filename = path_leaf(file.name)
  new_files = _files_in_dir(dir, old_files)
  new_file_name = _get_best_file_match(filename, new_files)
  if new_file_name is not None:
    log('Fuzzy found file rotated: {0}', new_file_name)
    new_file = open(join(dir, new_file_name), 'rb')
    _close(file)
    return new_file
  return None


def _close(file):
  try:
    file.close()
  except Exception as ex:
    log('An exception occurred while trying to close the file: {0}.', str(ex))


def _try_reopen_if_rotated(file, size):
  log('Trying to reopen {0}.', file.name)
  new_size = stat(file.name).st_size
  if new_size == size:
    log('File not rotated.')
    return None
  if new_size > size:
    log('File size increased: check rotated')
    pos = file.tell()
    file.seek(pos)
    bytes = file.read(1)
    if bytes is not None and len(bytes) > 0:
      log('File not rotated, seek to {0}', pos)
      file.seek(pos)
      return None
  log('size={0}, new_size={1}.', size, new_size)
  log('File rotated. reopening.')
  _close(file)

  new_file = open(file.name, 'rb')
  return new_file


def log_tail(filename, fuzzy_rotation):
  files = _files_in_dir(dirname(filename))
  size = stat(filename).st_size
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
        file, pos, size, files = _open_if_log_rotated(file, pos, size, files, fuzzy_rotation)
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


def _slicklog_tail(remote_logger, logfile, suppress_print, fuzzy_rotation):
  for message in log_tail(logfile, fuzzy_rotation):
    if not suppress_print:
      print(message, end="")
    remote_logger.log(message)


def slicklog_tail(logfile, api_key, log_group_name, log_name, endpoint, suppress_print, fuzzy_rotation):
  wait_interval = __MIN_WAIT
  remote_logger = _build_remote_logger(api_key, log_group_name, log_name, endpoint)
  while True:
    try:
      _slicklog_tail(remote_logger, logfile, suppress_print, fuzzy_rotation)
    except Exception as ex:
      log('An error occurred while running {0}: {1}', __TOOL_NAME, str(ex))
      wait_interval = _wait(wait_interval)
