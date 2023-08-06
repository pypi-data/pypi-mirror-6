import docker
import docker.auth

from sbdk.error import SbdkError
from .runner import Runner, ImageRunner
from .shell import Shell, Bash, SSH
from .utils import find_image, parse_repository_tag
from sbgsdk.util import import_name


def make_client(project, **kwargs):
    if project.context.get('docker_client_class'):
        cls = import_name(project.context.get('docker_client_class'))
        return cls(project, **kwargs)

    args = {'base_url': project.docker_daemon_url,
            'version': project.docker_protocol_version}
    args.update(kwargs)
    docker_client = docker.Client(**args)
    return docker_client


def make_runner(project, **kwargs):
    if project.project_data:
        return Runner(make_client(project), project, **kwargs)
    return ImageRunner(make_client(project), project, **kwargs)


def make_shell(project, **kwargs):
    kind = project.shell_type
    if kind == 'bash':
        args = {'docker': make_runner(project)}
        args.update(kwargs)
        return Bash(project, **args)
    elif kind == 'ssh':
        return Bash(project, **kwargs)
    else:
        raise SbdkError("Unknown shell: '%s'" % kind)

