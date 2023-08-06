__version__ = '0.2.10'
# Copyright (c) 2013. SlickLog.
__author__ = 'Torindo Nesci'

from atexit import register
from threading import Thread
from threading import Lock
from time import sleep
from time import time

from .util import log
from .util import u
from .util import new_queue
from .util import queue_mod
from .util import httplib_mod
from .util import quote_p
from .util import os_platform


class ConnectionBuilder:

  __DEFAULT_ENDPOINT = 'https://api.slicklog.com/u/log'
  __HTTP = 'http'
  __HTTPS = 'https'
  __HTTP_METHOD = 'PUT'
  __HTTP_TIMEOUT = 30
  __HTTP_PORT = 443
  __HTTP_CONTENT_TYPE_HEADER = 'Content-Type'
  __HTTP_CONTENT_TYPE_VALUE = 'text/plain; charset=utf-8'
  __HTTP_CONTENT_LENGTH_HEADER = 'Content-Length'
  __HTTP_USER_AGENT_HEADER = 'User-Agent'
  __HTTP_USER_AGENT_VALUE = 'PyRemoteLogger ' + __version__ + ': ' + os_platform()
  __API_KEY = 'apiKey'
  __LOG_GROUP_NAME = 'logGroupName'
  __LOG_NAME = 'logName'
  __QUERY_STRING = __API_KEY + '={0}&' + __LOG_GROUP_NAME + '={1}&' + __LOG_NAME + '={2}'

  def __init__(self, api_key, log_group_name, log_name, endpoint=None):
    if endpoint is None:
      endpoint = ConnectionBuilder.__DEFAULT_ENDPOINT
    self.api_key = u(api_key).encode('utf8')
    self.log_group_name = u(log_group_name).encode('utf8')
    self.log_name = u(log_name).encode('utf8')
    self.protocol,\
        self.host,\
        self.port,\
        self.path = self._get_endpoint_parts(endpoint)
    self._print_endpoint()

  def _print_endpoint(self):
    log(' -- Endpoint --')
    log(' host => {0}', self.host)
    log(' port => {0}', self.port)
    log(' path => {0}', self.path)

  @staticmethod
  def _get_endpoint_parts(endpoint):
    endpoint = str(endpoint)
    if endpoint.lower().startswith(ConnectionBuilder.__HTTP + '://'):
      protocol = ConnectionBuilder.__HTTP
    elif endpoint.lower().startswith(ConnectionBuilder.__HTTPS + '://'):
      protocol = ConnectionBuilder.__HTTPS
    else:
      err = 'The http protocol expected is either {0} or {1}. Found {2}.'\
          .format(ConnectionBuilder.__HTTP, ConnectionBuilder.__HTTPS, endpoint)
      raise ValueError(err)
    endpoint = endpoint[len(protocol) + len('://'):]
    host = endpoint
    port = ConnectionBuilder.__HTTP_PORT
    path = ''
    path_idx = endpoint.find('/')
    if path_idx >= 0:
      host = endpoint[0:path_idx]
      path = endpoint[path_idx:]
      if path.endswith('/'):
        path = path[0:-1]
    port_idx = host.find(':')
    if port_idx >= 0:
      port = int(host[port_idx + 1:])
      host = host[0:port_idx]

    return protocol, host, port, path

  def new_connection(self, length):
    url = self.path
    q = self._build_query_string()
    url = url + '?' + q
    log('Creating new connection to {0}://{1}:{2}{3}', self.protocol, self.host, self.port, url)
    if self.protocol == ConnectionBuilder.__HTTPS:
      conn = httplib_mod().HTTPSConnection(self.host, self.port, timeout=ConnectionBuilder.__HTTP_TIMEOUT)
    else:
      conn = httplib_mod().HTTPConnection(self.host, self.port, timeout=ConnectionBuilder.__HTTP_TIMEOUT)
    try:
      conn.connect()
      conn.putrequest(ConnectionBuilder.__HTTP_METHOD, url)
      conn.putheader(ConnectionBuilder.__HTTP_CONTENT_TYPE_HEADER, ConnectionBuilder.__HTTP_CONTENT_TYPE_VALUE)
      conn.putheader(ConnectionBuilder.__HTTP_CONTENT_LENGTH_HEADER, '{0}'.format(length))
      conn.putheader(ConnectionBuilder.__HTTP_USER_AGENT_HEADER, ConnectionBuilder.__HTTP_USER_AGENT_VALUE)
      conn.endheaders()
    except Exception as ex:
      log('Connection error: {0}', str(ex))
      res = conn.getresponse()
      log('Connection Response: {0}, {1}, {2}', str(res.status), str(res.reason), str(res.read()))
      raise ex
    log('Connection Created')
    return conn

  def _build_query_string(self):
    return ConnectionBuilder.__QUERY_STRING.format(
        quote_p(self.api_key), quote_p(self.log_group_name), quote_p(self.log_name))


class SlickLogRemoteLogger:

  __REMOTE_LOGGER_SPAWNER_THREAD_NAME = 'SlicklLogRemoteLoggerSpawner'
  __REMOTE_LOGGER_THREAD_NAME = 'SlicklLogRemoteLogger'
  __PUSH_MAX_WAIT_SECS = 10
  __PUSH_MAX_RETRY = 6
  __MAX_QUEUE_SIZE = 100000
  __MAX_SEND_SIZE = 410000
  __MAX_QUEUE_WAIT = 10
  __MIN_QUEUE_WAIT = 1
  __BUFER_SIZE = 16384
  __CHAR_ENCODING = 'utf8'
  __HTTP_RESPONSE_OK = 200
  __HEADER_ERROR = 'SlickLogErrorDescription'

  def __init__(self, conn_builder, spawn_new_threads=False, daemon_thread=False):
    if not daemon_thread:
      self.lock = Lock()
    else:
      self.lock = None
    self.shutdown_now = False
    self.conn_builder = conn_builder
    self.log_queue = new_queue(SlickLogRemoteLogger.__MAX_QUEUE_SIZE)
    self.spawn_new_threads = spawn_new_threads and daemon_thread
    self.data_pushed = 0
    thread = Thread(target=SlickLogRemoteLogger._get_and_push_messages, args=(self,))
    thread.setName(SlickLogRemoteLogger.__REMOTE_LOGGER_SPAWNER_THREAD_NAME)
    thread.setDaemon(daemon_thread)
    thread.start()
    self.spawning_thread = thread

    register(SlickLogRemoteLogger.shutdown_hook, self)
    log('{0} initialized: version {1}.', SlickLogRemoteLogger.__name__, __version__)

  def shutdown(self):
    self.shutdown_now = True

  def log(self, message):
    if self.shutdown_now:
      log('{0} in shutdown', SlickLogRemoteLogger.__name__)
      return
    try:
      bytes = u(message).encode(SlickLogRemoteLogger.__CHAR_ENCODING)
      self.log_queue.put_nowait(bytes)
      log('message put int queue: {0}', message)
    except queue_mod().Full as ex:
      log('Log queue is full, cleaning: {0}.', str(ex))
      with self.log_queue.mutex:
        self.log_queue.queue.clear()

  def flush(self):
    pass

  def close(self):
    log('Closing')
    self.shutdown_now = True

  def shutdown_hook(self):
    log('Shutdown hook called')
    self.shutdown_now = True
    log('Starting Finalizer')
    try:
      has_data = True
      while has_data:
        size = self._collect_and_push(greedy=True)
        has_data = size > 0
    except Exception as ex:
      log('An exception occurred while pushing record in finalizer: {0}:{1}.', ex.__class__, str(ex))
      self.data_pushed = 0

  def _get_and_push_messages(self):
    wait = 0.010
    while not self.shutdown_now:
      try:
        if not self.spawn_new_threads:
          self._push_next_messages()
        else:
          log('Spawning new thread.')
          worker_thread = Thread(target=SlickLogRemoteLogger._push_next_messages, args=(self,))
          worker_thread.setName(SlickLogRemoteLogger.__REMOTE_LOGGER_THREAD_NAME)
          worker_thread.setDaemon(False)
          worker_thread.start()
          worker_thread.join()
          sleep(0.001)
        if self.data_pushed > 0:
          wait = 0.010
        else:
          log('No Data pushed. Sleeping {0}secs', wait)
          if self.shutdown_now:
            log('SlickLog Remote Logger is about to shutdown')
            return
          wait = self._wait(wait)
      except Exception as ex:
        log('An exception occurred while pushing record: {0}:{1}. sleeping {2}secs', ex.__class__, str(ex), wait)
        wait = self._wait(wait)

  def _push_next_messages(self):
    try:
      size = self._collect_and_push(greedy=False)
      self.data_pushed = size
    except Exception as ex:
      log('An exception occurred while pushing record: {0}:{1}.', ex.__class__, str(ex))
      self.data_pushed = 0

  @staticmethod
  def _wait(wait):
    sleep(wait)
    wait *= 2
    if wait > SlickLogRemoteLogger.__PUSH_MAX_WAIT_SECS:
      wait = SlickLogRemoteLogger.__PUSH_MAX_WAIT_SECS
    return wait

  @staticmethod
  def _is_error_recoverable(code):
    code_class = '{0}xx'.format(str(code)[0])
    log('Http response code class is {0}.', code_class)
    return code_class != '4xx' and code_class != '2xx'

  @staticmethod
  def _close_connection(conn):
    if conn is None:
      return True
    try:
      log("Closing connection.")
      response = conn.getresponse()
      reason = 'success'
      if response.status != SlickLogRemoteLogger.__HTTP_RESPONSE_OK:
        reason = response.getheader(SlickLogRemoteLogger.__HEADER_ERROR)
      log("Http status code is {0}, reason={1}", response.status, reason)
      conn.close()
      if response.status == SlickLogRemoteLogger.__HTTP_RESPONSE_OK:
        return True
      return not SlickLogRemoteLogger._is_error_recoverable(response.status)
    except Exception as ex:
      log('An error occurred while closing connection: {0}', repr(ex))
      return False

  def _timeout_passed(self, start_time, greedy):
    now = time()
    elapsed = now - start_time
    log('Elapsed from connection start {0}secs', elapsed)
    return elapsed >= SlickLogRemoteLogger.__MAX_QUEUE_WAIT or (self.shutdown_now and not greedy)

  def _poll(self, start_time, greedy):
    max_wait = 0
    if not greedy:
      now = time()
      max_wait = SlickLogRemoteLogger.__MAX_QUEUE_WAIT - (now - start_time)
    try:
      wait = min(max_wait, SlickLogRemoteLogger.__MIN_QUEUE_WAIT)
      elapsed = 0
      polling_start = time()
      while elapsed <= max_wait:
        log("Waiting on queue {0}secs.", wait)
        data = self.log_queue.get(True, wait)
        if data is not None or self.shutdown_now:
          return data
        elapsed = time() - polling_start
    except queue_mod().Empty:
      log('Queue is empty. Wait timeout expired')
      return None

  def _acquire_lock(self):
    lock = self.lock
    if lock is not None:
      lock.acquire()

  def _release_lock(self):
    lock = self.lock
    if lock is not None:
      lock.release()

  def _collect(self, greedy):
    self._acquire_lock()
    try:
      size = 0
      buf = []
      max_size = SlickLogRemoteLogger.__MAX_SEND_SIZE
      start_time = time()
      while size < max_size and not self._timeout_passed(start_time, greedy):
        log('Getting message from queue')
        bytes = self._poll(start_time, greedy)
        if bytes is None:
          break
        buf.append(bytes)
        size += len(bytes)
        log('Collected message {0}', bytes)
      return buf, size
    finally:
      self._release_lock()

  def _collect_and_push(self, greedy):
    buf, size = self._collect(greedy)
    log('Collected messages of size {0}', size)
    if size <= 0:
      return 0
    bytes = b''.join(buf)
    try:
      conn = self._get_conn(size)
      log('Sending data, length:{0}.', size)
      conn.send(bytes)
      if self._close_connection(conn):
        return size
    except Exception as ex:
      log('An error occurred while sending log messages: {0}', repr(ex))
    if self._retry_send_bytes_on_error(bytes):
      return size
    return 0

  def _retry_send_bytes_on_error(self, bytes):
    success = False
    count = 0
    wait = 0.1
    while not success and count < SlickLogRemoteLogger.__PUSH_MAX_RETRY:
      try:
        log('Trying to re-send failed bytes, count={0}. waiting={1}', count, wait)
        wait = self._wait(wait)
        conn = self._get_conn(len(bytes))
        conn.send(bytes)
        success = self._close_connection(conn)
      except Exception as ex:
        log('An error occurred while re-sending log messages: {0}', repr(ex))
      finally:
         count += 1
    return success

  def _get_conn(self, length):
    return self.conn_builder.new_connection(length)
