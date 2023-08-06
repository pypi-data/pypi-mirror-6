import os

from sbdk.docker import make_runner, make_client
from sbdk.executor import Adun
from sbdk.error import SbdkError
from sbgsdk.job import Job
from sbgsdk.protocol import to_json, from_json


def argument_parser(subparsers):
    parser = subparsers.add_parser("cf", help="Run from CF")
    parser.set_defaults(func=run)

    parser.add_argument("--job", help="Path to JSON file with Job", type=str, required=True)
    parser.add_argument("--result", help="Path to future JSON file with result of job", type=str, required=True)
    parser.add_argument("--image-repo", help="Docker image repo", type=str, required=True)
    parser.add_argument("--image-tag", help="Docker image tag", type=str, required=True)


def find_image(client, image_id):
    images = client.images()
    return (filter(lambda x: x['Id'].startswith(image_id), images) or [None])[0]


def run(project, job, image_repo, image_tag, result):
    assert project and job and image_tag and image_repo and result, 'All arguments required.'
    job_file_path = job
    with open(job_file_path) as fp:
        job = from_json(fp)
        assert isinstance(job, Job), "Expected Job in %s" % job_file_path

    docker_client = make_client(project)
    image = find_image(docker_client, image_tag)
    if not image:
        docker_client.pull(image_repo, image_tag)
        image = find_image(docker_client, image_tag)
    if not image:
        raise SbdkError('Image not found: %s tag: %s' % (image_repo, image_tag))
    os.chdir(project.project_dir)
    project.context['image_id'] = image['Id']
    executor = Adun(make_runner(project))
    r = executor.exec_wrapper_job(job)
    with open(result, 'w') as fp:
        to_json(r, fp)
