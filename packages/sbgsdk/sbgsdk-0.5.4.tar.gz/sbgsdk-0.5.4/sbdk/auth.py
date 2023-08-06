import getpass
import json
import requests
import logging

from sbdk.error import SbdkError


def login(project, retries=2):
    if retries < 0:
        raise SbdkError('Login failed')
    url = project.schema_server_url + '/auth'
    usr = raw_input("Username: ")
    if not usr:
        return login(project, retries-1)
    pwd = getpass.getpass()
    resp = push_json(url, {'username': usr, 'password': pwd}, None, no_raise_for=[401, 402])
    if resp.status_code in (401, 402):
        print('Sorry. Try again.')
        return login(project, retries-1)
    return usr, resp.json()['session_id']


def push_url(project, user):
    return project.schema_server_url + '/repo/' + user + '/' + project.name + '/image'


def push_json(url, data, session_id, no_raise_for=tuple()):
    headers = {'Content-Type': 'application/json'}
    if session_id:
        headers['session-id'] = session_id
    response = requests.post(url, json.dumps(data), headers=headers)
    if response.status_code not in no_raise_for:
        response.raise_for_status()
    return response
