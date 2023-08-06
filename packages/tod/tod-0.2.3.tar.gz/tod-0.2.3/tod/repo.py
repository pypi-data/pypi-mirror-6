import os
import sys

from ConfigParser import SafeConfigParser
from copy import deepcopy
from termcolor import colored

from tod.links import expand

def parse_repo_mapping(args):
    parser = SafeConfigParser()
    parser.read(args.mapping_file)
    mapping = {}
    for s in parser.sections():
        mapping[s] = {c[0]:c[1] for c in parser.items(s)}
    return mapping


def is_git_dir(path):
    if not os.path.isdir(os.path.join(path, '.git')):
        return False
    return True


def check_section(args):
    if not args.mapping.get(args.section, None):
        print colored('Section does not exist.', 'red')
        sys.exit(1)


def check_names(args):
    for name in args.names:
        if not args.mapping.get(args.section, {}).get(name, None):
            print colored('Link "%s" does not exist.' % name, 'red')
            sys.exit(1)
