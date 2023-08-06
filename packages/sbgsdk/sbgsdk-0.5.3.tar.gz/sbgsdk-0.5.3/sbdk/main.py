#!/usr/bin/env python

import sys
import argparse
import logging

from sbdk.commands import init, push, test, sh, run, show_settings, schema, fix_uid, upload
from sbdk.error import SbdkError
from sbdk.project import Project
from sbdk import VERSION


def main(argv=None, context=None):

    context = context or {}
    parser = argparse.ArgumentParser(description="Seven Bridges Wrapper SDK Tool",
                                     epilog="Try 'sbdk [COMMAND] -h' for command specific options",
                                     prog="sbg",
                                     version=VERSION)
    parser.add_argument('--project-dir', default='',
                        help='Use this dir instead of project dir.')
    parser.add_argument('--verbose', '-V', default=False, action='store_true',
                        help='Increase output verbosity')

    subparsers = parser.add_subparsers()
    commands = [init, test, push, sh, run, show_settings, schema, fix_uid, upload]
    for cmd in commands:
        cmd.argument_parser(subparsers)

    args = vars(parser.parse_args(argv))

    level = logging.DEBUG if args.pop('verbose') else logging.INFO
    logging.basicConfig(stream=sys.stderr, level=level)

    context['project_dir'] = args.pop('project_dir')
    project = Project(context)

    f = args.pop('func')
    underscored = dict([(k.replace('-', '_'), v) for k, v in args.items()])
    try:
        f(project, **underscored)
    except SbdkError as e:
        print(e.message)
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
