import logging
import urllib
from grow.common import config
from grow.common import utils


class Error(Exception):
  pass


class LatestVersionCheckError(Error):
  pass


def get_this_version():
  return config.VERSION


def get_latest_version():
  logging.info('Checking for updates to the Grow SDK...')
  version_manifest = 'https://raw.github.com/grow/pygrow/master/grow/VERSION'
  try:
    version = urllib.urlopen(version_manifest).read()
    return version.strip()
  except Exception as e:
    text = 'Could not check for updates to the SDK. Are you online?'
    logging.error(utils.colorize('{red}%s{/red}' % text))
    raise LatestVersionCheckError(str(e))


def check_version(quiet=False):
  try:
    theirs = get_latest_version()
    yours = config.VERSION
    if theirs > yours:
      logging.info('---')
      logging.info(utils.colorize('{green}Your version: %s,{/green} {yellow}latest version: %s{/yellow}' % (yours, theirs)))
      logging.info('A newer version of the SDK is available, so please update yours. See http://growsdk.org.')
      if utils.is_packaged_app():
        logging.info('Quick update by pasting the following command:')
        command = '  python -c "$(curl -fsSL https://raw.github.com/grow/pygrow/master/install.py)"'
        logging.info(utils.colorize('{yellow}%s{/yellow}' % command))
      else:
        logging.info('Update using: pip install --upgrade grow')
      logging.info('---')
    else:
      logging.info('You have the latest version: {}'.format(yours))
  except LatestVersionCheckError:
    if not quiet:
      raise
