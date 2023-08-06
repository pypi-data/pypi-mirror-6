# Copyright (c) 2013. SlickLog.
__author__ = 'Torindo Nesci'

import ConfigParser
import argparse
from argparse import RawTextHelpFormatter
import os
import signal

from slicklog.util import set_debug

from .tail import slicklog_tail


__TOOL_NAME = "slicklogtail"
__SLICKLOG = "slicklog"
__SLICKLOG_API_KEY = "api_key"
__SLICKLOG_LOG_GROUP_NAME = "log_group_name"
__SLICKLOG_LOG_NAME = "log_name"
__SLICKLOG_ENDPOINT = "endpoint"
__CONFIG_FILE = "config_file"
__LOGFILE = "logfile"
__VERBOSE = "verbose"
__FUZZY_ROTATION = "fuzzy_rotation"
__SUPPRESS_PRINT = "suppress_print"

__TOOL_DESCRIPTION = """\
Listens to a log file and transfers the appended data to SlickLog.com.
The tool can take the SlickLog configuration from the command line
or from a configuration file.
Usage examples:
 {0} --{1} WlHfkJOgIEnSX3tD --{2} 'My Log Group' --{3} 'My Log' /logs/mylog.log
 {4} --{5} /conf/slicklog.cofig /logs/mylog.log
""".format(__TOOL_NAME, __SLICKLOG_API_KEY, __SLICKLOG_LOG_GROUP_NAME, __SLICKLOG_LOG_NAME,
           __TOOL_NAME, __CONFIG_FILE)

__CONFIG_FILE_DESCRIPTION = """\
SlickLog configuration file.
SlickLogTail can take the configuration from
the configuration file or from the command line.
In this file insert api_key, log_group_name and log name.
This is an example:

[{0}]
{1} = WlHfkJOgIEnSX3tD
{2} = This my log group
{3} = This is my log name

""".format(
    __SLICKLOG,
    __SLICKLOG_API_KEY,
    __SLICKLOG_LOG_GROUP_NAME,
    __SLICKLOG_LOG_NAME)


def _check_option_exists(config, filename, section, option):
  if not config.has_option(section, option):
    print("No option {0} in section [{1}] in config file {2}.".format(
          option, section, filename))
    exit(0)


def _check_config_file(config, filename):
  if not config.has_section(__SLICKLOG):
    print("No section [{0}[ in config file {1}.".format(__SLICKLOG, filename))
    exit(0)
  _check_option_exists(config, filename, __SLICKLOG, __SLICKLOG_API_KEY)
  _check_option_exists(config, filename, __SLICKLOG, __SLICKLOG_LOG_GROUP_NAME)
  _check_option_exists(config, filename, __SLICKLOG, __SLICKLOG_LOG_NAME)


def _read_config_file(filename):
  config = ConfigParser.RawConfigParser()
  config.read(filename)

  _check_config_file(config, filename)

  api_key = config.get(__SLICKLOG, __SLICKLOG_API_KEY)
  log_group_name = config.get(__SLICKLOG, __SLICKLOG_LOG_GROUP_NAME)
  log_name = config.get(__SLICKLOG, __SLICKLOG_LOG_NAME)
  endpoint = None
  if config.has_option(__SLICKLOG, __SLICKLOG_ENDPOINT):
    endpoint = config.get(__SLICKLOG, __SLICKLOG_ENDPOINT)

  return api_key, log_group_name, log_name, endpoint


def _check_not_none(prop, val):
  if val is None or len(val) == 0:
    print('{0} is not defined.'.format(prop))
    exit(0)


def _get_config(args):
  if args.config_file is not None:
    if not os.path.isfile(args.config_file):
      print('The configuration file {0} does not exist.'.format(args.config_file))
      exit(0)
    return _read_config_file(args.config_file)
  api_key = args.api_key
  log_group_name = args.log_group_name
  log_name = args.log_name
  endpoint = args.endpoint

  _check_not_none(__SLICKLOG_API_KEY, api_key)
  _check_not_none(__SLICKLOG_LOG_GROUP_NAME, log_group_name)
  _check_not_none(__SLICKLOG_LOG_NAME, log_name)

  return api_key, log_group_name, log_name, endpoint


def main():
  parser = argparse.ArgumentParser(description=__TOOL_DESCRIPTION, formatter_class=RawTextHelpFormatter)
  parser.add_argument(__LOGFILE, help='The log file path to listen to.')
  parser.add_argument('--' + __SLICKLOG_API_KEY, help='SlickLog api key.')
  parser.add_argument('--' + __SLICKLOG_LOG_GROUP_NAME, help='SlickLog log group.')
  parser.add_argument('--' + __SLICKLOG_LOG_NAME, help='SlickLog log.')
  parser.add_argument('--' + __SLICKLOG_ENDPOINT, help='SlickLog log RESTful API endpoint. For internal use only.')
  parser.add_argument('--' + __CONFIG_FILE, help=__CONFIG_FILE_DESCRIPTION)
  parser.add_argument('--' + __FUZZY_ROTATION, default=False, action='store_true',
                      help='Use fuzzy logic to detect the rotated file.')
  parser.add_argument('--' + __SUPPRESS_PRINT, default=False, action='store_true',
                      help='Suppress the print of the appended data to the log file.')
  parser.add_argument('--' + __VERBOSE, default=False, action='store_true', help='Verbose mode.')
  args = parser.parse_args()

  if not os.path.isfile(args.logfile):
    print('{0} does not exits.'.format(args.logfile))
    exit(0)

  set_debug(args.verbose)
  api_key, log_group_name, log_name, endpoint = _get_config(args)

  print(' -- Running on Configuration --')
  print('  {0} => {1}'.format(__LOGFILE, args.logfile))
  print('  {0} => {1}'.format(__SLICKLOG_LOG_GROUP_NAME, log_group_name))
  print('  {0} => {1}'.format(__SLICKLOG_LOG_NAME, log_name))
  print('  {0} => {1}'.format(__SUPPRESS_PRINT, args.suppress_print))
  print('  {0} => {1}'.format(__FUZZY_ROTATION, args.fuzzy_rotation))
  print('  {0} => {1}'.format(__VERBOSE, args.verbose))

  signal.signal(signal.SIGINT, _signal_handler)

  slicklog_tail(
      args.logfile,
      api_key,
      log_group_name,
      log_name,
      endpoint,
      args.suppress_print,
      args.fuzzy_rotation)


def _signal_handler(signal, frame):
    print 'Exiting'
    exit(0)


if __name__ == "__main__":
  main()
