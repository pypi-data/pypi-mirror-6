import json
import keyword
import os
import re
import stat
import random
import time
from os.path import join, isdir, dirname, basename, abspath, isfile

import sbdk.resources as resources
from sbdk.state import State
from sbdk.error import SbdkError
from sbdk import VERSION


DEFAULT_CONFIG = {
    'version': VERSION,
    'default_base_image': 'sevenbridges/sdkbase:beta',
    'logging_config': 'logging.json',

    'shell_type': 'bash',
    'pip_options': '-q --download-cache /sb/pip_cache',
    'sdk_runner_command': ['/usr/bin/python', '-m', 'sbgsdk.cli'],
    'schema_server_url': 'https://hatchery.sbgenomics.com',
    'file_server_url': 'fs.sbgenomics.com',
    'vs_client_path': '/opt/vsclient/bin/vsclient.sh',

    'docker_registry_name': 'images.sbgenomics.com',
    'docker_registry_version': '1',
    'docker_registry_schema': 'https',
    'docker_daemon_url': 'unix://var/run/docker.sock',
    'docker_protocol_version': '1.8',
    'docker_user': 'sbg',
    'docker_dns': None,
    'docker_entrypoint': ['/sbin/my_init', '--quiet', '--']  # '--enable-insecure-key',
}


class Project(object):
    def __init__(self, context=None):
        context = context or {}
        self.sb_home = os.path.expanduser('~/.sbg')
        self._prepare_home_dir()

        pd = context.get('project_dir')
        if pd:
            pd = abspath(pd)
            if isdir(pd):
                self.project_dir = pd
            else:
                raise SbdkError("Directory does not exist: " + pd)
        else:
            cwd = context.get('cwd', '.')
            self.project_dir = find_project_dir(cwd)

        if not self.project_dir and context.get('is_test'):
            self.project_dir = '.'

        self.project_data = None
        self.state = None

        if self.project_dir:
            project_data = join(self.project_dir, '.sbdk')
            if isdir(project_data):
                self.project_data = project_data
                self.state = State(self.project_data)

        self.context = self._create_context(context)

    def _get_image_id(self):
        if self.context.get('image_id'):
            return self.context.get('image_id')
        elif self.state:
            return self.state.get('image_id')
        return None

    def _set_image_id(self, val):
        self.context['image_id'] = val

    image_id = property(_get_image_id, _set_image_id)

    def initialize(self, path, base_image=None):
        self.project_dir = abspath(destination(self.context.get('cwd', '.'), path))
        self.project_data = join(self.project_dir, '.sbdk')
        base_image = base_image or self.default_base_image

        if not isdir(self.project_data):
            os.makedirs(self.project_data)

        base = basename(self.project_dir)
        self.state = State(self.project_data)
        self.state['project_name'] = sanitize_project_name(base)
        self.state['image_id'] = base_image
        self.state.save()

    @property
    def base_cmd(self):
        log_conf = None
        if self.project_data:
            log_conf = join(self.project_data, self.context['logging_config'])
        if log_conf and isfile(log_conf):
            return self.context['sdk_runner_command'] + ['--logging-config',
                                                         join('.sbdk', self.context['logging_config'])]
        return self.context['sdk_runner_command']

    @property
    def name(self):
        name = None
        if self.state:
            name = self.state.get('project_name', None)
        if (not name) and self.project_dir:
            name = sanitize_project_name(basename(self.project_dir))
            if self.state:
                self.state['project_name'] = name
                self.state.save()
        return name

    @property
    def top_level(self):
        raise NotImplementedError()

    @property
    def docker_registry_url(self):
        return '{0}://{1}/v{2}/'.format(self.docker_registry_schema,
                                        self.docker_registry_name,
                                        self.docker_registry_version)

    def __getattr__(self, item):
        if item in DEFAULT_CONFIG:
            return self.context[item]
        else:
            raise AttributeError("%r object has no attribute %r" %
                                (self.__class__.__name__, item))

    def _prepare_home_dir(self, retries=5):
        try:
            if not os.path.exists(self.sb_home):
                os.mkdir(self.sb_home)

            cache_path = join(self.sb_home, 'pip_cache')
            utils_path = join(self.sb_home, 'utils')

            for p in cache_path, utils_path:
                if not os.path.exists(p):
                    os.mkdir(p)

            resources.copy('fix-uid.sh', utils_path)
            fix_uid = join(utils_path, 'fix-uid.sh')
            mod = os.stat(fix_uid).st_mode
            plus_x = stat.S_IXGRP | stat.S_IXUSR | stat.S_IXOTH
            os.chmod(fix_uid, mod | plus_x)
        except OSError:
            if retries:
                time.sleep(random.random())
                return self._prepare_home_dir(retries-1)
            raise

    def _create_context(self, context=None):
        result = dict(DEFAULT_CONFIG)
        global_settings = join(self.sb_home, 'settings.json')
        if isfile(global_settings):
            with open(global_settings) as fp:
                result.update(json.load(fp))
        if self.project_data:
            project_settings = join(self.project_data, 'settings.json')
            if isfile(project_settings):
                with open(project_settings) as fp:
                    result.update(json.load(fp))
        result.update(context or {})
        return result


def destination(cwd, path):
    dst = os.path.join(cwd, path).rstrip('/')
    if os.path.isdir(dst) and os.listdir(dst):
        raise SbdkError("Can't initialize project in non-empty dir '%s'" % dst)
    return dst


def find_project_dir(start_dir='.'):
    cd = abspath(start_dir)
    project_dir = None
    while cd != '/':
        if isdir(join(cd, '.sbdk')):
            project_dir = cd
            break
        cd = dirname(cd)
    return project_dir


def sanitize_project_name(name):
    project_name = name.replace('-', '_').lower()

    valid = (not keyword.iskeyword(project_name)) and \
        re.match('^[a-z][a-z0-9_]*$', project_name)

    if not valid:
        raise SbdkError("Invalid project name. Project name must be a valid Python identifier")
    return project_name
