import json

from sbgsdk.job import Job
from sbdk.executor import Adun
from sbgsdk.protocol import to_json
from sbdk.docker import make_runner
from sbdk.commands import check_image, check_project_dir


def argument_parser(subparsers):
    parser = subparsers.add_parser("run", help="Run wrapper")
    parser.set_defaults(func=run)

    parser.add_argument("wrapper", help="Wrapper name", type=str)
    parser.add_argument("args", help="Load wrapper args from this JSON file", type=str)
    parser.add_argument("--output", "-o", help="Save wrapper output to this JSON file", type=str)
    # parser.add_argument("--one-container", help="Run all the jobs from single container", type=bool)


def run(project, wrapper, args, output=None, one_container=True):
    check_project_dir(project)
    check_image(project)
    r = make_runner(project)
    with open(args) as fp:
        job = Job(wrapper, args=json.load(fp))
    try:
        result = Adun(r).execute(job, one_container)
        if output:
            with open(output, 'w') as fp:
                to_json(result, fp)
        else:
            print(to_json(result))
    finally:
        r.chown()
