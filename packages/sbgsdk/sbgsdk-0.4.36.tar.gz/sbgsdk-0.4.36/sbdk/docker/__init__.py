import docker
import docker.auth

from sbdk.error import SbdkError
from .runner import Runner, ImageRunner
from .shell import Shell, Bash, SSH
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


def find_image(docker_client, image_id):
    images = docker_client.images()
    repo_name = None
    try:
        registry, repo_name = docker.auth.resolve_repository_name(image_id)
    except:
        pass

    def flt(x):
        x['Id'].startswith(image_id) or x['Repository'] == repo_name

    return (filter(flt, images) or [None])[0]


def ensure_image(docker_client, image):
    img = find_image(docker_client, image)
    if not img:
        docker_client.pull(image)
    # hope for the best
