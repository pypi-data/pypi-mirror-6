import datetime
import logging
import os
import zipfile
from grow.deployments import base


class ZipFileDeployment(base.BaseDeployment):

  def get_destination_address(self):
    return self.filename

  def set_params(self, storage, out_dir, out_file=None):
    self.storage = storage
    if out_dir and out_file is None:
      basename = datetime.datetime.now().strftime('%Y-%m-%d.%H%M%S') + '.zip'
      self.filename = os.path.join(out_dir, basename)
    else:
      self.filename = os.path.expanduser(out_file)

  def prelaunch(self):
    dirname = os.path.dirname(self.filename)
    if not os.path.exists(dirname):
      os.makedirs(dirname)
    logging.info('Creating zip file to: {}'.format(self.filename))

  def deploy(self, pod):
    self.prelaunch()

    fp = self.storage.open(self.filename, 'w')
    zip_file = zipfile.ZipFile(fp, mode='w')

    paths_to_content = pod.dump()
    for path, content in paths_to_content.iteritems():
      if isinstance(content, unicode):
        content = content.encode('utf-8')
      zip_file.writestr(path, content)

    zip_file.close()
    fp.close()
    return self.filename

  def snapshot(self, pod):
    self.prelaunch()

    fp = self.storage.open(self.filename, 'w')
    zip_file = zipfile.ZipFile(fp, mode='w')

    for path in pod.list_dir('/'):
      content = pod.read_file(path)
      if isinstance(content, unicode):
        content = content.encode('utf-8')
      zip_file.writestr(path, content)

    zip_file.close()
    fp.close()
    return self.filename
