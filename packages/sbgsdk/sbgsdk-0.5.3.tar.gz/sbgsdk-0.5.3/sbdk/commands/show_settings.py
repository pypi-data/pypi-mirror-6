import json


def argument_parser(subparsers):
    parser = subparsers.add_parser("show-settings", help="Show project configuration")
    parser.set_defaults(func=show)


def show(project):
    print(json.dumps(project.context, indent=2))
