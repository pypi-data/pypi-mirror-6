from sbdk.commands import check_image
from sbdk.docker import make_runner


def argument_parser(subparsers):
    parser = subparsers.add_parser("schema", help="Show schema (JSON) for all wrappers in project")

    parser.set_defaults(func=schema)


def schema(project):
        check_image(project)
        docker = make_runner(project)
        docker.schema()
