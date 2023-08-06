from dataplicity import constants
from dataplicity.client import settings

from ConfigParser import SafeConfigParser

from fs.utils import copyfile, copydir
from fs.errors import ResourceNotFoundError

import os
from os.path import basename, join


from fnmatch import fnmatch
from logging import getLogger

log = getLogger('dataplicity')


DEFAULT_FIRMWARE_CONF = """
[firmware]
version = 1
exclude = *.pyc
    __*__
    .*
    .hg
    .git

"""


def _get_list(value):
    return [line.strip() for line in value.split('\n')]


def get_conf(src_fs):
    cfg = SafeConfigParser()
    with src_fs.open('dataplicity.conf') as f:
        cfg.readfp(f)
    return cfg


def get_version(src_fs):
    if not src_fs.exists('firmware.conf'):
        src_fs.setcontents('firmware.conf', DEFAULT_FIRMWARE_CONF)
    cfg = SafeConfigParser()
    with src_fs.open('firmware.conf') as f:
        cfg.readfp(f)
    version = int(cfg.get('firmware', 'version'))
    return version


def bump(src_fs):
    version = int(get_version(src_fs))
    new_version = version + 1
    cfg = SafeConfigParser()
    with src_fs.open('firmware.conf') as f:
        cfg.readfp(f)
    cfg.set('firmware', 'version', str(new_version))
    with src_fs.open('firmware.conf', 'wb') as f:
        cfg.write(f)
    print "firmware version bumped to {:04}".format(new_version)
    return new_version


def build(src_fs, dst_fs):
    """Build a firmware"""
    if not src_fs.exists('firmware.conf'):
        src_fs.setcontents('firmware.conf', DEFAULT_FIRMWARE_CONF)

    cfg = SafeConfigParser()
    with src_fs.open('firmware.conf') as f:
        cfg.readfp(f)

    version = int(cfg.get('firmware', 'version'))
    exclude = _get_list(cfg.get('firmware', 'exclude'))

    def wildcard(path):
        return not any(fnmatch(basename(path), wildcard) for wildcard in exclude)

    for file_path in src_fs.walkfiles(wildcard=wildcard, dir_wildcard=wildcard):
        copyfile(src_fs, file_path, dst_fs, file_path)

    return version


def install(device_class, version, firmware_fs, dst_fs):
    """Install a firmware"""
    dst_path = join(device_class, str(version))
    if not dst_fs.exists(dst_path):
        dst_fs.makedir(dst_path, allow_recreate=True, recursive=True)
    install_fs = dst_fs.opendir(dst_path)
    copydir(firmware_fs, install_fs, overwrite=True)
    return dst_fs.getsyspath(dst_path)


def activate(device_class, version, dst_fs):
    """Make a given version active"""
    dst_path = join(device_class, str(version))
    firmware_path = dst_fs.getsyspath(dst_path)
    current_path = os.path.join(constants.FIRMWARE_PATH, 'current')
    try:
        # Remove old symlink
        os.remove(current_path)
    except OSError:
        pass
    try:
        os.symlink(firmware_path, current_path)
    except:
        log.exception('unable to link current firmware')


def get_ui(firmware_fs):
    """Get ui (xml) data from firmware"""
    with firmware_fs.open('dataplicity.conf', 'rb') as f:
        conf = settings.read_from_file(f)
    ui_path = conf.get('register', 'ui')
    try:
        return firmware_fs.getcontents(ui_path)
    except ResourceNotFoundError:
        return None
