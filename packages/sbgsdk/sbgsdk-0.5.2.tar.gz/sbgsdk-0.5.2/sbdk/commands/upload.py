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
        print('Uploader location or file server URL missing.')
        sys.exit(1)
    if not os.path.isfile(file):
        print('%s is not a file.' % file)
        sys.exit(1)
    file = os.path.abspath(file)
    usr, sid = login(project)
    user_home = '/home/%s' % usr
    dest = os.path.join(user_home, os.path.basename(file))
    cwd = os.path.abspath('.')
    args = [executable, '-o', 'u', '-sessionId', '-s', server, '-ssl', '-lf', file, '-rf', dest]
    logging.debug('Running cmd: %s', args)
    os.chdir('/tmp')
    try:
        p = Popen(args, stdin=PIPE)
        p.communicate('%s\n' % sid)
    finally:
        os.chdir(cwd)