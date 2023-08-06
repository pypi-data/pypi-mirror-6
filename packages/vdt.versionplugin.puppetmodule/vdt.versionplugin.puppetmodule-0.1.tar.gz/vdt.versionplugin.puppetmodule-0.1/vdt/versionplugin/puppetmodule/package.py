import logging

from os.path import basename
from os import getcwd

from vdt.versionplugin.puppetmodule.shared import create_package


log = logging.getLogger('vdt.versionplugin.puppetmodule.package')

def build_package(version):
    """
    Build package out of a puppet module.
    """
    log.debug("Building puppet module version {0} with fpm.".format(version))
    with version.checkout_tag:
        full_name = basename(getcwd())
        short_name = full_name.replace('puppet-', '')
        create_package(full_name, short_name, str(version), version.extra_args)


def set_package_version(version):
    """
    If there need to be modifications to source files before a
    package can be built (changelog, version written somewhere etc.)
    that code should go here
    """
    log.debug("set_package_version is not implemented for puppetmodule")
