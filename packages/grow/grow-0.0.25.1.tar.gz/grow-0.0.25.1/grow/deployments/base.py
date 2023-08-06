"""A base class for a deployment.

A deployment takes a pod, builds a static fileset from it, and deploys it to a
remote location, suitable for serving the web site to live end users.
Currently, Grow only supports static deployments, however, this may change as
Grow implements requirements such as "password protection" and geolocation.

The deployment process generally works like this:

  (1) A pod is exported, creating a dictionary mapping file paths to content.
  (2) A connection is made between Grow and the destination.
  (3) An index is retrieved from the destination, which contains a mapping
      of file paths to a sha-1 hash value of the file's content.
  (4) An index is generated locally, and the local index is compared to the
      index at the destination. This allows Grow to produce a diff between
      the local ("canary") fileset and the destination's fileset.
  (5) An integration test (if any) is performed.
  (6) If the deployment is a dry run, the process ends here.
  (7) Any required pre-launch configuration to the destination is applied.
  (8) The diff between the canary fileset and the destination fileset is
      applied.
  (9) An updated index is written to the destination.
  (10) Any required post-launch configuration to the destination is applied.
       The deployment is complete.

All deployments follow this process, and the BaseDeployment class takes
care of most of the hard work and business logic. So if you're adding a new
deployment, you'll just have to implement the following methods:

  delete_file(self, path)
    Deletes a file at the destination, given the file's pod path.

  get_destination_address(self):
    Returns the address of the destination (used to show the user where
    the pod has been deployed to).

  read_file(self, path)
    Reads a file at the destination, returning the file's content.

  write_file(self, path, content)
    Writes a file at the destination, given the file's pod path and its content.

The following methods are optional to implement:

  postlaunch(self)
    Performs any post-launch tasks.

  prelaunch(self)
    Performs any pre-launch configuration/tasks.

  set_params(self, **kwargs)
    Sets any parameters required by the other subclassed methods.

  write_index_at_destination(self, new_index):
    Writes the index of the newly-built pod to the destination.

Once you've written a new deployment, add it to this directory's __init__.py.

To make the deployment available from the command line "grow deploy" utility,
you must modify the DeployCmd class in pygrow/grow/commands.py.
"""

import logging
import time
import unittest
from grow.pods import index
from grow.common import utils


class Error(Exception):
  pass


class NotFoundError(Error, IOError):
  pass


class DeploymentTestCase(unittest.TestCase):
  deployment = None


class BaseDeployment(object):

  test_case_class = DeploymentTestCase

  # TODO(jeremydw): Args to set_params and init should be switched.
  # init should have the params which make deployment objects fully-capable.
  # set_params should set optional params like dry_run and confirm.
  def __init__(self, *args, **kwargs):
    self.dry_run = kwargs.get('dry_run', False)
    self.confirm = kwargs.get('confirm', False)

  def read_file(self, path):
    """Returns a file-like object."""
    raise NotImplementedError

  def write_file(self, path, content):
    raise NotImplementedError

  def get_destination_address(self):
    raise NotImplementedError

  def set_params(self, **kwargs):
    pass

  def run_tests(self):
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(self.test_case_class)
    for test_case in suite:
      test_case.deployment = self
    unittest.TextTestRunner().run(suite)

  def write_index_at_destination(self, new_index):
    self.write_file(index.Index.BASENAME, new_index.to_yaml())

  def get_index_at_destination(self):
    path = index.Index.BASENAME
    try:
      content = self.read_file(path)
      logging.info('Loaded index at destination.')
      return index.Index.from_yaml(content)
    except IOError:
      logging.info('No index found at destination, assuming new deployment.')
      return index.Index()

  def postlaunch(self):
    logging.info('Deployed to: {}'.format(self.get_destination_address()))
    logging.info('Done in {}s!'.format(time.time() - self.start_time))

  def prelaunch(self):
    self.run_tests()

  def deploy(self, pod):
    logging.info('Deploying to: {}'.format(self.get_destination_address()))
    self.prelaunch()

    deployed_index = self.get_index_at_destination()
    paths_to_content = pod.dump()
    new_index = index.Index()
    new_index.update(paths_to_content)
    diffs = new_index.diff(deployed_index)
    if not diffs:
      text = utils.colorize('{white}Diff is empty, nothing to launch, aborted.{/white}')
      logging.info(text)
      return

    if self.dry_run:
      return

    if self.confirm:
      diffs.log_pretty()
      if not utils.interactive_confirm('Proceed with launch?'):
        logging.info('Launch aborted.')
        return

    self.start_time = time.time()
    index.Index.apply_diffs(diffs, paths_to_content, write_func=self.write_file,
                            delete_func=self.delete_file)
    # TODO(jeremydw): Index should only be updated if the diff was entirely
    # successfully applied.
    self.write_index_at_destination(new_index)
    logging.info('Wrote index: /{}'.format(index.Index.BASENAME))

    self.postlaunch()
    return diffs
