import os
import sys
import logging
from subprocess import Popen, PIPE

from sbdk.auth import login


def argument_parser(subparsers):
    parser = subparsers.add_parser("upload", help="Upload a file to sbgenomics.")
    parser.set_defaults(func=upload)

    parser.add_argument("file", type=str, help="Local path of file to upload")


def upload(project, file):
    executable = project.vs_client_path
    server = project.file_server_url
    if not executable or not server:
        print 'Uploader location or file server URL missing.'
        sys.exit(1)
    usr, sid = login(project)
    user_home = '/home/%s' % usr
    dest = os.path.join(user_home, os.path.basename(file))
    args = [executable, '-o', 'u', '-sessionId', '-s', server, '-ssl', '-lf', file, '-rf', dest]
    logging.debug('Running cmd: %s', args)
    p = Popen(args, stdin=PIPE)
    p.communicate('%s\n' % sid)