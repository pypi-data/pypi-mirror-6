from __future__ import print_function
from __future__ import division
# Copyright (c) 2013. SlickLog.
__author__ = 'Torindo Nesci'

import sys
import traceback
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
MIN_WAIT = 0.01
MAX_WAIT = 5


class Tail:

  __READ_SIZE = 1024
  __FILE_SIMILARITY_TH = 0.95
  __LEIV_DIST_TH = 0.50

  def __init__(self, filename, fuzzy_rotation=False, charset='utf-8'):
    self.fuzzy_rotation = fuzzy_rotation
    self.dir = dirname(filename)
    self.file = open(filename, 'rb')
    self.size = stat(filename).st_size
    self.files = self._files_in_dir()
    self.pos = 0
    log('{0}, size: {1}', filename, self.size)
    self.file.seek(self.size)
    self.charset = charset

  def _files_in_dir(self, exclude_files_set=None):
    dir = self.dir
    if exclude_files_set is None:
      exclude_files_set = set()
    if dir is None or len(dir) == 0:
      dir = '.'
    log('listing files in dir:{0} with exclude files:{1}', dir, exclude_files_set)
    files = set()
    for f in listdir(dir):
      if isfile(join(dir, f)) and f not in exclude_files_set:
        files.add(f)
    if is_debug_enabled():
      for f in files:
        log(' file found in dir {0}: {1}', dir, f)
    return files

  @staticmethod
  def _get_best_file_match(filename, files):
    chars, mod = to_vect(filename)
    min_dist = sys.maxint
    min_file = None
    for f in files:
      similarity = cos_similarity(chars, mod, f)
      log('Similarity between {0} and {1} is {2}.', filename, f, similarity)
      if similarity > Tail.__FILE_SIMILARITY_TH:
        dist = levenshtein_distance(filename, f)
        edit_perc = dist / len(filename)
        log('Levenshtein distance between {0} and {1} is {2}, perc edit is {3}.', filename, f, dist, edit_perc)
        if edit_perc < Tail.__LEIV_DIST_TH and dist < min_dist:
          min_dist = dist
          min_file = f
    return min_file

  def _open_if_log_rotated(self):
    wait_interval = MIN_WAIT
    while True:
      try:
        try:
          rotated = self._try_reopen_if_rotated()
          if rotated:
            self.files = self._files_in_dir()
            return
        except OSError as err:
          log('An error occurred while reopening log {0}: {1}.', self.file.name, repr(err))
          if err.errno != errno.ENOENT or not self.fuzzy_rotation:
            raise err
        if self.fuzzy_rotation:
          fuzzy_rotated = self._try_reopen_if_fuzzy_rotated()
          if fuzzy_rotated:
            self.files = self._files_in_dir()
            return
        return
      except Exception as ex:
        log('An exception occurred while opening rotated log: {0}.', repr(ex))
        wait_interval = _wait(wait_interval)

  def _try_reopen_if_rotated(self):
    log('Trying to reopen {0}.', self.file.name)
    new_size = stat(self.file.name).st_size
    if new_size == self.size:
      log('File not rotated.')
      return False
    if new_size > self.size:
      log('File size increased: check rotated')
      old_pos = self.pos
      self.file.seek(old_pos)
      bytes = self.file.read(1)
      if bytes is not None and len(bytes) > 0:
        log('File not rotated, seek to {0}', old_pos)
        self.file.seek(old_pos)
        return False
    log('size={0}, new_size={1}.', self.size, new_size)
    log('File rotated. reopening.')
    self._close(self.file)

    self.file = open(self.file.name, 'rb')
    self.pos = 0
    self.size = 0
    return True

  @staticmethod
  def path_leaf(path):
    head, tail = split(path)
    return tail or basename(head)

  def _try_reopen_if_fuzzy_rotated(self):
    dir = dirname(self.file.name)
    if dir is None or len(dir) == 0:
      dir = '.'
    filename = self.path_leaf(self.file.name)
    new_files = self._files_in_dir(exclude_files_set=self.files)
    new_file_name = self._get_best_file_match(filename, new_files)
    if new_file_name is not None:
      log('Fuzzy found file rotated: {0}', new_file_name)
      new_file = open(join(dir, new_file_name), 'rb')
      self._close(self.file)
      self.file = new_file
      self.pos = 0
      self.size = 0
      return True
    return False

  @staticmethod
  def _close(file):
    try:
      file.close()
    except Exception as ex:
      log('An exception occurred while trying to close the file: {0}.', repr(ex))

  def log_tail(self):
    wait_interval = MIN_WAIT
    while True:
      self.pos = self.file.tell()
      bytes = self.file.read(Tail.__READ_SIZE)
      if bytes is None or len(bytes) == 0:
        log('no new data.')
        wait_interval = _wait(wait_interval)
        if wait_interval == MAX_WAIT:
          self._open_if_log_rotated()
        self.file.seek(self.pos)
      else:
        self.size += len(bytes)
        str = bytes.decode(self.charset)
        log('Read {0}', bytes)
        yield str
        wait_interval = MIN_WAIT


def _wait(interval):
  log('Sleeping {0}secs.', interval)
  sleep(interval)
  interval *= 2
  if interval > MAX_WAIT:
    interval = MAX_WAIT
  return interval


def _build_remote_logger(api_key, log_group_name, log_name, endpoint=None):
  conn_builder = ConnectionBuilder(api_key, log_group_name, log_name, endpoint)
  return SlickLogRemoteLogger(conn_builder, spawn_new_threads=False, daemon_thread=True)


def _slicklog_tail(remote_logger, tail, suppress_print, charset):
  for message in tail.log_tail():
    if not suppress_print:
      print(message.encode(charset), end="")
    remote_logger.log(message)


def slicklog_tail(logfile, api_key, log_group_name, log_name, endpoint, suppress_print, fuzzy_rotation, charset):
  wait_interval = MIN_WAIT
  remote_logger = _build_remote_logger(api_key, log_group_name, log_name, endpoint)
  tail = Tail(logfile, fuzzy_rotation, charset)
  while True:
    try:
      _slicklog_tail(remote_logger, tail, suppress_print, charset)
    except Exception as ex:
      ex_format = traceback.format_exc()
      log('An error occurred while running {0}: {1} / {2}', __TOOL_NAME, str(ex), ex_format)
      wait_interval = _wait(wait_interval)
