from sbdk.commands import check_image, check_project_dir
from sbdk.docker import make_runner


def argument_parser(subparsers):
    parser = subparsers.add_parser("test", help="Test wrapper")
    parser.set_defaults(func=test)
    parser.add_argument("module", help="Python module with tests. E.g. 'sbg_wrappers.my_wrapper'. "
                                       "Same as nosetests '--where'", type=str, default='.')


def test(project, module):
    check_project_dir(project)
    check_image(project)
    r = make_runner(project)
    try:
        r.run_tests(module)
    finally:
        r.chown()


__test__ = False

