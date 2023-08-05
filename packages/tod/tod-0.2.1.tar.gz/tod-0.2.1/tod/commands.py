import os
import sys
import subprocess
from termcolor import colored
from tod.links import printable_status
from tod.links import expand
from tod.links import expand_source
from tod.links import status as link_status
from tod.links import UNLINKED
from tod.links import CONFLICT
from tod.links import MISSING
from tod.links import LINKED
from tod.links import MAX_STATUS
from tod.repo import is_git_dir
from tod.repo import check_section
from tod.repo import check_names


def link(args):
    check_section(args)
    if args.all:
        names = args.mapping[args.section].keys()
    else:
        check_names(args)
        names = args.name

    for name in names:
        dst = expand(args.mapping[args.section][name])
        src = expand_source(args.repo, name)
        s = link_status(src, dst)
        if s == UNLINKED:
            os.symlink(src, dst)
            print colored('Linked: %s to %s' % (src, dst), 'green')
        elif s == LINKED:
            print colored('Already Linked: %s' % src, 'yellow')
        elif s == MISSING:
            print colored('Source Missing: %s' % src, 'yellow')
        elif s == CONFLICT:
            print colored('Conflict: %s' % src, 'red')


def unlink(args):
    """Unlink the file/folder from the config repo to the filesystem."""
    check_section(args)
    if args.all:
        names = args.mapping[args.section].keys()
    else:
        check_names(args)
        names = args.name

    for name in names:
        dst = expand(args.mapping[args.section][name])
        src = expand_source(args.repo, name)
        s = link_status(src, dst)
        if s == LINKED:
            os.unlink(dst)
            print colored('Unlinked: %s to %s' % (src, dst), 'green')
        elif s == UNLINKED:
            print colored('Already Unlinked: %s' % src, 'yellow')
        elif s == CONFLICT:
            print colored('Conflict: %s' % src, 'red')


def status(args):
    """Display the status of all config mappings."""
    if args.sections:
        for section in args.sections:
            if args.mapping.get(section, None):
                print colored(
                    'Specified section "%s" does not exist.' % section, 'red')
                sys.exit(1)

    sections = args.sections if args.sections else args.mapping.keys()

    for section in sections:
        mapper = args.mapping[section]
        out = []
        out.append(section)
        out.append('-' * len(section))
        max_source = max([len(m) for m in mapper])
        for src, dst in mapper.iteritems():
            s = link_status(expand_source(args.repo, src), expand(dst))
            line = [
                printable_status(s.rjust(MAX_STATUS)),
                src.ljust(max_source),
                colored(' -> ', 'blue'),
                dst
            ]
            out.append(' '.join(line))
        print '\n'.join(out)


def edit(args):
    """Open the mapping.ini for editing with $EDITOR."""
    mapping_file = args.mapping_file
    editor = expand('$EDITOR')
    subprocess.call([editor, mapping_file])


def git(args):
    """Pass all arguments to git for execution."""
    if not is_git_dir(args.repo):
        print colored('Dot file directory is not tracked via git.', 'red')
        sys.exit(1)
    args.git_args.insert(0, 'git')
    output = subprocess.check_output(args.git_args, cwd=args.repo)
    print output
