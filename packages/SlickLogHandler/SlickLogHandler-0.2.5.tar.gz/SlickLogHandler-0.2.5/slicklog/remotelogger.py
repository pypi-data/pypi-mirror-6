# Copyright (c) 2013. SlickLog.
__author__ = 'Torindo Nesci'

from threading import Thread
from time import sleep
from time import time

from slicklog.util import log
from slicklog.util import u
from slicklog.util import new_queue
from slicklog.util import queue_mod
from slicklog.util import httplib_mod
from slicklog.util import quote_p


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
  __HTTP_CONTENT_LENGTH_VALUE = '512000'
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

  def new_connection(self):
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
      conn.putheader(ConnectionBuilder.__HTTP_CONTENT_LENGTH_HEADER, ConnectionBuilder.__HTTP_CONTENT_LENGTH_VALUE)
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

  __CONN_TIMEOUT = 20
  __REMOTE_LOGGER_SPAWNER_THREAD_NAME = 'SlicklLogRemoteLoggerSpawner'
  __REMOTE_LOGGER_THREAD_NAME = 'SlicklLogRemoteLogger'
  __PUSH_MAX_WAIT_SECS = 10
  __PUSH_MAX_RETRY = 6
  __MAX_QUEUE_SIZE = 100000
  __MAX_SEND_SIZE = 410000
  __MAX_QUEUE_WAIT = 1
  __BUFER_SIZE = 16384
  __CHAR_ENCODING = 'utf8'

  def __init__(self, conn_builder, spawn_new_threads=False, deamon_thread=False):
    self.shutdown_now = False
    self.conn_builder = conn_builder
    self.log_queue = new_queue(SlickLogRemoteLogger.__MAX_QUEUE_SIZE)
    self.spawn_new_threads = spawn_new_threads and deamon_thread
    self.data_pushed = 0
    thread = Thread(target=SlickLogRemoteLogger._get_and_push_messages, args=(self,))
    thread.setName(SlickLogRemoteLogger.__REMOTE_LOGGER_SPAWNER_THREAD_NAME)
    thread.setDaemon(deamon_thread)
    thread.start()
    self.spawning_thread = thread

    log('{0} initialized.', SlickLogRemoteLogger.__name__)

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

  def _get_and_push_messages(self):
    wait = 0.010
    while True:
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
          sleep(wait)
          wait = self._wait(wait)
      except Exception as ex:
        log('An exception occurred while pushing record: {0}:{1}. sleeping {2}secs', ex.__class__, str(ex), wait)
        sleep(wait)
        wait = self._wait(wait)

  def _push_next_messages(self):
    try:
      size = self._collect_and_push()
      self.data_pushed = size
    except Exception as ex:
      log('An exception occurred while pushing record: {0}:{1}.', ex.__class__, str(ex))
      self.data_pushed = 0

  @staticmethod
  def _wait(wait):
    wait *= 2
    if wait > SlickLogRemoteLogger.__PUSH_MAX_WAIT_SECS:
      wait = SlickLogRemoteLogger.__PUSH_MAX_WAIT_SECS
    return wait

  @staticmethod
  def _close_connection(conn):
    try:
      if conn is not None:
        log("Closing connection.")
        conn.close()
    except Exception as ex:
      log('An error occurred while closing connection: {0}', str(ex))

  @staticmethod
  def _timeout_passed(conn, start_time):
    if conn is None:
      return False
    now = time()
    elapsed = now - start_time
    log('Elapsed from connection start {0}secs', elapsed)
    return elapsed >= SlickLogRemoteLogger.__CONN_TIMEOUT

  def _collect_and_push(self):
    conn = None
    try:
      max_size = SlickLogRemoteLogger.__MAX_SEND_SIZE
      max_buf = SlickLogRemoteLogger.__BUFER_SIZE
      buf_size = 0
      size = 0
      start_time = time()
      buf = []
      while size < max_size and not self._timeout_passed(conn, start_time):
        try:
          log('Getting message from queue')
          bytes = self.log_queue.get(True, SlickLogRemoteLogger.__MAX_QUEUE_WAIT)
          log('pushing message {0}', bytes)
        except queue_mod().Empty:
          log('Queue is empty. Wait timeout expired')
          break
        buf.append(bytes)
        size += len(bytes)
        buf_size += len(bytes)
        if buf_size >= max_buf:
          conn = self._send_buffer(conn, buf)
          buf_size = 0
          buf = []
          start_time = time()
      if buf_size > 0:
        conn = self._send_buffer(conn, buf)
      log('Sent {0} bytes', size)
      return size
    finally:
      self._close_connection(conn)

  def _get_conn(self, conn):
    if conn is None:
      return self.conn_builder.new_connection()
    return conn

  def _send_buffer(self, conn, buf):
    try:
      bytes = b''.join(buf)
      conn = self._get_conn(conn)
      conn.send(bytes)
      log('Pushed new buffer')
      return conn
    except Exception as ex:
      log('An exception occurred while pushing buffer: {0}', str(ex))
      with self.log_queue.mutex:
        self.log_queue.queue.appendleft(b''.join(buf))
      raise ex
