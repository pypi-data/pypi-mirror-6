import argparse
import yaml

from vdt.version.shared import VersionError


def parse_version_extra_args(version_args):
    p = argparse.ArgumentParser(description="Package builder for puppet forge.")
    p.add_argument('--modulename', help="puppet forge module name")
    p.add_argument('--version', help="puppet forge required version")
    args, extra_args = p.parse_known_args(version_args)
    
    if args.modulename is None:
        raise VersionError("puppetforge requires --modulename to be specified.")
    
    return args, extra_args

class RubyYaml(object):
    def __init__(self, yaml):
        yaml.add_multi_constructor(u"!ruby/object:", self.construct_ruby_object)
        yaml.add_constructor(u"!ruby/sym", self.construct_ruby_sym)
        self.yaml = yaml

    def construct_ruby_object(self, loader, suffix, node):
        return loader.construct_yaml_map(node)

    def construct_ruby_sym(self, loader, node):
        return loader.construct_yaml_str(node)

    def load(self, stream):
        return self.yaml.load(stream)
