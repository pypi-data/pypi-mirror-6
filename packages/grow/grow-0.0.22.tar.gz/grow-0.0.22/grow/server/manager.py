import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from grow.pods.preprocessors.file_watchers import file_watchers
from grow.server import handlers
from grow.server import main as main_lib
from paste import httpserver
from paste import translogger
import atexit
import multiprocessing
import os
import sys
import threading
import yaml

_servers = {}
_config_path = '{}/.grow/servers.yaml'.format(os.environ['HOME'])


def _loop_watching_for_changes(pod, file_watchers_to_preprocessors, quit_event):
  while not quit_event.is_set():
    for file_watcher, preprocessors in file_watchers_to_preprocessors.iteritems():
      if file_watcher.has_changes():
        [preprocessor.run() for preprocessor in preprocessors]
    quit_event.wait(timeout=1.5)


def _start(pod, host=None, port=None, use_simple_log_format=True):
  root = pod.root
  preprocessors = pod.list_preprocessors()

  # Map directory names to preprocessors.
  dirs_to_preprocessors = {}
  for preprocessor in preprocessors:
    for watched_dir in preprocessor.list_watched_dirs():
      if watched_dir not in dirs_to_preprocessors:
        dirs_to_preprocessors[watched_dir] = []
      dirs_to_preprocessors[watched_dir].append(preprocessor)

  # Run all preprocessors for the pod.
  [preprocessor.run() for preprocessor in preprocessors]

  # Create file watchers for each preprocessor.
  file_watchers_to_preprocessors = {}
  for dirname, preprocessors in dirs_to_preprocessors.iteritems():
    dirname = os.path.join(pod.root, dirname.lstrip('/'))
    change_watcher = file_watchers.get_file_watcher([dirname])
    change_watcher.start()
    file_watchers_to_preprocessors[change_watcher] = preprocessors

  # Start a thread where preprocessors can run if there are changes.
  quit_event = threading.Event()
  change_watcher_thread = threading.Thread(
      target=_loop_watching_for_changes,
      args=(pod, file_watchers_to_preprocessors, quit_event))
  change_watcher_thread.start()

  root = os.path.abspath(os.path.normpath(root))
  logging.info('Serving pod with root: {}'.format(root))
  logger_format = ('[%(time)s] "%(REQUEST_METHOD)s %(REQUEST_URI)s" %(status)s'
                   if use_simple_log_format else None)

  # Start the actual server.
  handlers.set_pod_root(root)
  app = main_lib.application
  app = translogger.TransLogger(app, format=logger_format)
  httpserver.serve(app, host=host, port=port)

  # Clean up once serve exits.
  quit_event.set()
  change_watcher_thread.join()
  sys.exit()


def start(pod, host=None, port=None, use_subprocess=False):
  root = pod.root
  if root in _servers:
    logging.error('Server already started for pod: {}'.format(root))
    return

  if not use_subprocess:
    _start(pod, host=host, port=port)
    return

  server_process = multiprocessing.Process(target=_start, args=(root, host, port))
  server_process.start()
  _servers[root] = server_process
  return server_process


def stop(root):
  process = _servers.pop(root, None)
  if process is None:
    return
  try:
    process.terminate()
    logging.info('Stopped server for pod: {}'.format(root))
  except AttributeError:
    logging.info('Server already stopped for pod: {}'.format(root))


@atexit.register
def stop_all():
  for root in _servers.keys():
    stop(root)


def write_config(config):
  path = os.path.dirname(_config_path)
  if not os.path.exists(path):
    os.makedirs(path)
  content = yaml.dump(config, default_flow_style=False)
  fp = open(_config_path, 'w')
  fp.write(content)
  fp.close()


class PodServer(object):

  def __init__(self, root, port=8000, revision_status=None):
    self.root = root
    self.port = port
    self.revision_status = revision_status
    self.server_status = 'off'
    self._process = None

  def start(self):
    self._process = start(self.root, port=self.port, use_subprocess=True)
    self.server_status = 'on'
    logging.info('Started server for pod: {}'.format(self.root))

  def stop(self):
    self.server_status = 'off'
    try:
      self._process.terminate()
      logging.info('Stopped server for pod: {}'.format(self.root))
    except AttributeError:
      logging.info('Server already stopped.')

  def set_root(self, root):
    self.root = root

  def set_port(self, port):
    self.port = port

  @property
  def is_started(self):
    return self.server_status == 'on'

  @classmethod
  def load(cls):
    servers = []
    try:
      fp = open(_config_path)
      for server in yaml.load(fp)['servers']:
        servers.append(cls(
            server['root'],
            port=server.get('port'),
            revision_status=server.get('revision_status')
        ))
    except IOError:
      # .grow/servers.yaml does not exist.
      pass
    return servers
