import logging
import subprocess
import glob
import tempfile
import shutil

from os import getcwd, chdir
from os.path import join

from vdt.versionplugin.puppetforge.shared import parse_version_extra_args
from vdt.versionplugin.puppetmodule.shared import create_package


log = logging.getLogger('vdt.versionplugin.puppetmodule.package')

def build_package(version):
    """
    Build package out of a puppet module.
    """
    args, extra_args = parse_version_extra_args(version.extra_args)
    
    install_dir = tempfile.mkdtemp()
    pwd = getcwd()

    try:
        # install the module
        cmd = ['puppet', 'module', 'install', args.modulename,
                '--target-dir=%s' % install_dir,
                '--version=%s' % version]
        subprocess.check_call(cmd)
        
        # build the package
        modulename = version.userdata['name']
        moduledir = join(install_dir, modulename)
        chdir(moduledir)

        create_package("puppet-%s" % modulename, modulename, str(version), extra_args)

        for deb in glob.glob("*.deb"):
            shutil.move(join(moduledir, deb), "%s/" % pwd)
    finally:
        chdir(pwd)
        shutil.rmtree(install_dir)


def set_package_version(version):
    """
    If there need to be modifications to source files before a
    package can be built (changelog, version written somewhere etc.)
    that code should go here
    """
    log.debug("set_package_version is not implemented for puppetmodule")
