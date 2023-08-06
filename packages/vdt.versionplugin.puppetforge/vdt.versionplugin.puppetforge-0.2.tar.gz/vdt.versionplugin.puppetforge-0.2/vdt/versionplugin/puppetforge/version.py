"""
This file contains only functions that deal with the version
of the repository. It can set a new version as a tag and look
up the current version.
"""
import subprocess
import logging
import yaml
import operator

from vdt.version.shared import VersionError, VersionNotFound, Version

from vdt.versionplugin.puppetforge.shared import parse_version_extra_args, RubyYaml

log = logging.getLogger('vdt.versionplugin.puppetmodule.version')


__all__ = ('get_version', 'set_version')


def get_version(version_args):
    args, _ = parse_version_extra_args(version_args)
    cmd = ['puppet', 'module', 'search', args.modulename, '--render-as=yaml']
    
    log.debug("Running command: %s" % " ".join(cmd))
    
    output = subprocess.check_output(cmd).split('\n')

    if 'otice: Searching' in output[0]:
        output = "\n".join(output[1:])
    else:
        output = "\n".join(output)

    version = None

    rubyyaml = RubyYaml(yaml)
    results = rubyyaml.load(output)
    log.debug(output)

    if results.get('result') != 'success':
        raise VersionError("No puppet module found with name %s, reason: %s" % (args.modulename, output.get('result')))

    try:
        result = (item for item in results.get('answers') if item.get('full_name') == args.modulename).next()
        if args.version is not None:
            versions = map(operator.itemgetter('version'), result['releases'])
            log.debug("Available version: %s" % versions)

            if args.version not in versions:
                raise VersionNotFound("Version %s not found in %s. Available versions: %s" % (args.version, result['full_name'], versions))
            else:
                version = Version(args.version, extra_args=version_args, userdata=result)

        else:
            version = Version(result['version'], extra_args=version_args, userdata=result)

        log.debug("Version is: %(version)s" % result)
    except StopIteration:
        raise VersionError("No puppet module found with name %s" % args.modulename)

    assert(version)
    return version


def set_version(version):
    log.debug("set_version does nothing for puppetforge plugin.")
    return version
