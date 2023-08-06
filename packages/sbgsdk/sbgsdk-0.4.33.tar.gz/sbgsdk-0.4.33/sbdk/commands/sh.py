import sys

from sbdk.commands import check_image
from sbdk.docker import make_shell


def argument_parser(subparsers):
    parser = subparsers.add_parser("sh", help="Run shell in your image")
    parser.set_defaults(func=sh)

    parser.add_argument("--command", "-c", help="Command to execute", type=str)


def sh(project, command):
        check_image(project)
        shl = make_shell(project)

        if command:
            container = shl.run_command(command)
        else:
            container = shl.run_shell()

        ask_commit(container, project.state)


def ask_commit(container, save):
    sys.stdout.write("Do you want to commit this container? [Y/n]: ")
    while True:
        choice = sys.stdin.readline().lower().strip()
        if choice == '' or choice[0] == 'y':
            container.commit('', tag=False)
            if save:
                container.save_as_base()
            else:
                sys.stdout.write("Image id: {}".format(container.image['Id']))
            container.remove()
            return
        elif choice == 'n':
            return
        else:
            sys.stdout.write("Please enter 'y' or 'n': ")
