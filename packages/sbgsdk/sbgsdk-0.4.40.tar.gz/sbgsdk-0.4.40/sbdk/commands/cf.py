import os
import time
import random
import logging

from sbdk.docker import make_runner, make_client, find_image
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


def run(project, job, image_repo, image_tag, result):
    assert project and job and image_tag and image_repo and result, 'All arguments required.'
    job_file_path = job
    with open(job_file_path) as fp:
        job = from_json(fp)
        assert isinstance(job, Job), "Expected Job in %s" % job_file_path

    docker_client = make_client(project)
    image = get_image(docker_client, image_repo, image_tag)
    os.chdir(project.project_dir)
    project.context['image_id'] = image['Id']
    executor = Adun(make_runner(project, Volumes={'/mnt/ebs': {}}, __binds__={'/mnt/ebs': '/mnt/ebs:rw'}))
    r = executor.exec_wrapper_job(job)
    with open(result, 'w') as fp:
        to_json(r, fp)


def get_image(client, repo, tag, retries=5):
    logging.info('Searching for image %s:%s', repo, tag)
    img = find_image(client, repo, tag)
    if img:
        return img
    if retries < 1:
        raise SbdkError('Image not found: %s tag: %s' % (repo, tag))
    client.pull(repo, tag)
    time.sleep(1 + random.random() * 10)  # Weird stuff happening on simultaneous pull + run.
    return get_image(client, repo, tag, retries-1)