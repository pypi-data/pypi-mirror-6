import logging
import subprocess

from os import walk
from os.path import join, normpath

log = logging.getLogger('vdt.versionplugin.puppetmodule.shared')


def _build_config_files(name):
    list_of_files = []
    excludes = {}
    for (dirpath, dirnames, filenames) in walk('.'):
        dirpath = normpath(dirpath)
        for filename in filenames:
            if dirpath.startswith('.'):
                continue
            if filename.startswith('._'):
                continue
            if filename.startswith('.git'):
                excludes[filename] = True
            if dirpath.startswith('spec') or dirpath.startswith('test'):
                excludes['--exclude=%s' % join(dirpath, '*')] = True
            else:
                list_of_files.append(join(dirpath, filename))

    config_files = ['--config-files=%s' % \
        join('/etc/puppet/modules/', name, file) for file in list_of_files]
    return config_files, excludes.keys(), list_of_files


def create_package(full_name, short_name, version, extra_args):
    
    config_files, excludes, files = _build_config_files(short_name)
    cmd = ['fpm', '-s', 'dir',
           '--depends=puppet-common',
           '--prefix=/etc/puppet/modules/%s' % short_name,
           '--architecture=all',
           '--name=%s' % full_name,
           '--version=%s' % version] + config_files + excludes + extra_args + files
    log.debug("Running command %s" % " ".join(cmd))
    subprocess.check_call(cmd)
    