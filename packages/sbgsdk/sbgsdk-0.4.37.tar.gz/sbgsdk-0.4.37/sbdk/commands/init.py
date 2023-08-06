import os
import logging

import sbdk.resources as resources
from sbdk.commands.fix_uid import fix_uid


def argument_parser(subparsers):
    """ Setups parser for init subcommand """

    parser = subparsers.add_parser("init", help="Initialize project by populating project directory")
    parser.add_argument("project_name", type=str, default='',
                        help="Project name. It will be used as Python package name as well.")

    parser.add_argument("--base-image", "-b", type=str, default=None,
                        help="Base Docker image for new project")

    parser.add_argument("--example", "-e", default=False, action='store_true',
                        help="If this option is provided, project will be "
                             "populated with example working wrapper")
    parser.set_defaults(func=init)


def init(project, project_name, base_image, example):
    project.initialize(project_name, base_image)
    try:
        mkdirs(project, example)
        mkfiles(project, example)
        fix_uid(project, str(os.getuid()))
        logging.debug("Initialized project in %s", project.project_dir)
    except:
        # if os.path.isdir(project.project_dir):
        #     logging.debug("Removing created dir '%s'", project.project_dir)
        #     shutil.rmtree(project.project_dir)
        raise


def mkdirs(project, example):
    dst = project.project_dir
    top_level = os.path.join(dst, project.name)
    os.makedirs(top_level)
    os.makedirs(os.path.join(dst, 'test-data'))
    if example:
        os.makedirs(os.path.join(top_level, 'sleep'))
        os.makedirs(os.path.join(top_level, 'grep', 'test'))


def mkfiles(project, example):
    files = 'MANIFEST.in',
    dst = project.project_dir
    for f in files:
        with open(os.path.join(dst, f), 'w'):
            pass

    wrappers = resources.process_template('example-project/wrappers_entrypoint', project=project) if example else ""
    imports = resources.process_template('example-project/imports', project=project) if example else ""

    resources.process_template('init.py.tpl', os.path.join(dst, project.name, '__init__.py'),
                               project=project, imports=imports)
    resources.process_template('setup.py.tpl', os.path.join(dst, 'setup.py'),
                               project=project, wrappers=wrappers)
    resources.copy('logging.json', os.path.join(dst, '.sbdk', 'logging.json'))

    if example:
        packages = 'sleep', 'grep'
        file_names = '__init__.py', 'wrapper.py', 'schema.py', 'test.py'
        files = [(dir_name, file_name) for dir_name in packages for file_name in file_names]
        for f in files:
            dist_path = os.path.join(dst, project.name, f[0], f[1])
            resources.process_template('example-project/top_level/%s/%s.tpl' % f,
                                       dist_path,
                                       project=project)
        resources.copy('example-project/top_level/grep/test/words.txt',
                       os.path.join(dst, project.name, 'grep', 'test', 'words.txt'))
