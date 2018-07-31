from __future__ import print_function
import shutil
import logging
import os
import sys
import errno
from configobj import ConfigObj, ConfigObjError


try:
    basestring
except NameError:
    basestring = str


LOGGER = logging.getLogger(__name__)


def log(logger, level, message):
    """Logs message to stderr if logging isn't initialized."""

    if logger.parent.name != 'root':
        logger.log(level, message)
    else:
        print(message, file=sys.stderr)


def read_config_file(f):
    """Read a config file."""

    if isinstance(f, basestring):
        f = os.path.expanduser(f)

    try:
        config = ConfigObj(f, interpolation=False, encoding='utf8')
    except ConfigObjError as e:
        log(LOGGER, logging.ERROR, "Unable to parse line {0} of config file "
            "'{1}'.".format(e.line_number, f))
        log(LOGGER, logging.ERROR, "Using successfully parsed config values.")
        return e.config
    except (IOError, OSError) as e:
        log(LOGGER, logging.WARNING, "You don't have permission to read "
            "config file '{0}'.".format(e.filename))
        return None

    return config


def read_config_files(files):
    """Read and merge a list of config files."""

    config = ConfigObj()

    for _file in files:
        _config = read_config_file(_file)
        if bool(_config) is True:
            config.merge(_config)
            config.filename = _config.filename

    return config


def write_default_config(source, destination, overwrite=False):
    destination = os.path.expanduser(destination)

    dirname = os.path.dirname(destination)
    if not os.path.exists(dirname):
        mkdir_p(dirname)

    if not overwrite and os.path.exists(destination):
        return

    shutil.copyfile(source, destination)


def mkdir_p(path):
    "like `mkdir -p`"
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
