import json
import os.path
import requests
from sys import exit

from sbdk.auth import push_url, push_json
from sbdk.commands import check_project_dir, check_image, check_project_data
from sbdk.docker import make_runner


def argument_parser(subparsers):
    parser = subparsers.add_parser("push", help="Create new image and upload it")

    parser.set_defaults(func=push)

    parser.add_argument('message', help='Short description of your changes')


def push(project, message):
    check_project_dir(project)
    check_project_data(project)
    check_image(project)

    docker = make_runner(project)
    container = docker.run_install()
    if not container.is_success():
        print("Error while preparing image:")
        container.print_log()
        exit("Push command failed")
    config = {'Cmd': project.sdk_runner_command, 'Entrypoint': project.docker_entrypoint}
    container.load_credentials()
    container.commit(message, config).push()
    push_schema(project, container)
    container.remove()


def push_schema(project, container):
    data_dir = project.project_data
    # nulling project_data to force image runner
    project.project_data = None
    project.image_id = container.image['Id']
    runner = make_runner(project)
    runner.schema('.sbdk/schema.json')

    with open(os.path.join(data_dir, 'schema.json')) as fp:
        wrapper_data = json.load(fp)  # json.loads(self.docker.logs(c))

    if not wrapper_data:
        print('No wrappers registered (empty __init__.py?). Exiting.')
        exit(1)

    push_data = {'message': container.message or 'NO COMMIT MESSAGE',
                 'image_data': {'id': project.docker_registry_name + '/' + container.user + '/' + project.name,
                                'tag': container.tag},
                 'wrappers': wrapper_data}
    if project.schema_server_url:
        url = push_url(project, container.user)
        try:
            push_json(url, push_data, container.token)
        except requests.HTTPError as e:
            if e.response.status_code in (401, 402):
                container.load_credentials(renew=True)
                push_json(url, push_data, container.token)
            else:
                raise e