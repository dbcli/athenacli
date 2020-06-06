import shutil
import logging
import os
import sys
import errno
import boto3
from configobj import ConfigObj, ConfigObjError
from collections import defaultdict


try:
    basestring
except NameError:
    basestring = str


LOGGER = logging.getLogger(__name__)


class AWSConfig(object):
    def __init__(self, aws_access_key_id, aws_secret_access_key,
                 region, s3_staging_dir, profile, config):
        key = 'aws_profile %s' % profile
        try:
            _cfg = config[key]
        except:
            # this assumes that the profile is only known in the regular AWS config -> the boto lib will get it
            # from there. This is especially important if we have some kind of additional temporary session keys for
            # which the login fails if we set aws_access_key_id/aws_secret_access_key here
            _cfg = defaultdict(lambda: None)

        self.aws_access_key_id = self.get_val(aws_access_key_id, _cfg['aws_access_key_id'])
        self.aws_secret_access_key = self.get_val(aws_secret_access_key, _cfg['aws_secret_access_key'])
        self.region = self.get_val(region, _cfg['region'], self.get_region())
        self.s3_staging_dir = self.get_val(s3_staging_dir, _cfg['s3_staging_dir'])
        # enable connection to assume role
        self.role_arn = self.get_val(_cfg.get('role_arn'))

    def get_val(self, *vals):
        """Return the first True value in `vals` list, otherwise return None."""
        for v in vals:
            if v:
                return v

    def get_region(self):
        """Try to get region name from aws credentials/config files or environment variables"""
        return boto3.session.Session().region_name


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
