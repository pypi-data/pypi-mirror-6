import os
import logging

from sbdk.commands import check_image
from sbdk.docker import make_runner
from sbdk.error import SbdkError


def argument_parser(subparsers):
    parser = subparsers.add_parser("fix-uid", help="Sets UID of wrapper user inside image to match your host UID")
    parser.set_defaults(func=fix_uid)

    parser.add_argument("--uid", "-u", type=str, default=str(os.getuid()),
                        help="Set this UID instead of current user's uid")


def fix_uid(project, uid=None):
    check_image(project)
    r = make_runner(project)
    c = r.run(['/sb/utils/fix-uid.sh', project.docker_user, uid])
    if not c.is_success():
        c.print_log()
        raise SbdkError("Error while fixing UID.")

    c.commit(message="fix-uid")
    if project.state:
        c.save_as_base()
    else:
        project.context['image_id'] = c.image['Id']
    logging.info("UID for user '%s' set to %s", project.docker_user, uid)
    return c.image['Id']

