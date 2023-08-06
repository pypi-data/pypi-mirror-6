# Copyright (c) 2013. SlickLog.
__author__ = 'Torindo Nesci'

from logging import Handler

from slickloghandler.remotelogger import SlickLogRemoteLogger
from slickloghandler.remotelogger import ConnectionBuilder
from slickloghandler.util import log
from slickloghandler.util import is_debug_enabled
from slickloghandler.util import set_debug


DEFAULT_LOG_GROUP_NAME = 'Default Log Group'
DEFAULT_LOG_NAME = 'Default Log'


class SlickLogHandler(Handler):
  def __init__(self,
               api_key,
               log_group_name=DEFAULT_LOG_GROUP_NAME,
               log_name=DEFAULT_LOG_NAME,
               endpoint=None,
               debug=False,
               deamon_thread=True,
               spawn_new_threads=True):
    Handler.__init__(self)
    self.initialized = False
    set_debug(debug)
    conn_builder = ConnectionBuilder(api_key, log_group_name, log_name, endpoint)
    self.remote_logger = SlickLogRemoteLogger(
        conn_builder,
        deamon_thread=deamon_thread,
        spawn_new_threads=spawn_new_threads)
    self._print_conf(conn_builder, deamon_thread, spawn_new_threads)
    log('{0} initialized.', SlickLogHandler.__name__)
    self.initialized = True

  @staticmethod
  def _print_conf(conn_builder, deamon_thread, spawn_new_threads):
    log(' -- Handler Configuration --')
    log('  api_key => {0}', conn_builder.api_key)
    log('  log_group_name => {0}', conn_builder.log_group_name)
    log('  log_name => {0}', conn_builder.log_name)
    log('  debug => {0}', is_debug_enabled())
    log('  deamon_thread => {0}', deamon_thread)
    log('  spawn_new_threads => {0}', spawn_new_threads)

  @staticmethod
  def set_debug(debug):
    set_debug(debug)

  def flush(self):
    if self.initialized:
      self.remote_logger.flush()

  def close(self):
    Handler.close(self)
    if self.initialized:
      self.remote_logger.close()

  def emit(self, record):
    try:
      message = self.format(record)
      self.remote_logger.log(message)
      if not '\n' in message[-1]:
        self.remote_logger.log('\n')
    except Exception as ex:
      log('An error occurred while logging: {0}', str(ex))
      self.handleError(record)

  def shutdown(self):
    if self.initialized:
      self.remote_logger.shutdown()
