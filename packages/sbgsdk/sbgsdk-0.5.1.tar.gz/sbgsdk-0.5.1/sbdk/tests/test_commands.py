__author__ = 'luka'
import os
import shutil
import docker.auth

from sbdk.project import Project
from sbdk.docker import container
from sbdk.error import SbdkError
from sbdk.commands import init, push, test, sh, run, show_settings, schema, cf, fix_uid


BASE_CTX = {'docker_client_class': 'sbdk.tests.mock_client.MockClient'}


################################################
##
## (base_context, +id, +dir, +id+dir)
##  x (inside project dir, outside project dir)
##  x commands
##
################################################

NOTHING, IMAGE, DIR, STATE = 0, 1, 2, 4

ARGS = os.path.join(os.path.dirname(__file__), 'empty-args.json')


def run_adun(p):
    old = p.context['docker_client_class']
    try:
        p.context['docker_client_class'] = 'sbdk.tests.mock_client.OutJson'
        run.run(p, 'wrapper', ARGS, os.path.join(os.path.dirname(__file__), '__out__.json'), False)
        run.run(p, 'wrapper', ARGS, os.path.join(os.path.dirname(__file__), '__out__.json'), True)
    finally:
        p.context['docker_client_class'] = old


def run_push(p):
    if p.project_data:
        os.chdir(p.project_dir)
        with open('.sbdk/schema.json', 'w') as fp:
            fp.write('{}')
    push.push(p, 'message')


CMDS = {'run':      {'cmd': run_adun,
                     'depend': IMAGE | DIR},
        'fix-uid':  {'cmd': lambda p: fix_uid.fix_uid(p, '1000'),
                     'depend': IMAGE},
        'push':     {'cmd': run_push,
                     'depend': IMAGE | DIR | STATE},
        'schema':   {'cmd': schema.schema,
                     'depend': IMAGE},
        'show-settings': {'cmd': show_settings.show,
                          'depend': NOTHING},
        'test':     {'cmd': lambda p: test.test(p, '.'),
                     'depend': IMAGE | DIR}
}


def test_commands():
    container.push_json = lambda url, data, session_id: None
    docker.auth.auth.load_config = lambda: {'Configs': {p.docker_registry_url: {'Username': 'test', 'Password': 'test'}}}
    container.load_config = lambda: {'Configs': {p.docker_registry_url: {'Username': 'test', 'Password': 'test'}}}

    # test in project
    ctx = {'cwd': '/tmp/sbdk-test'}
    ctx.update(BASE_CTX)
    p = Project(ctx)
    try:
        p.initialize('prj_name')
        os.chdir(p.project_dir)

        for cmd in CMDS.itervalues():
            cmd['cmd'](p)
    finally:
        d = '/tmp/sbdk-test/prj_name'
        if os.path.isdir(d):
            shutil.rmtree(d)

    for conf in IMAGE, DIR, IMAGE | DIR:
        ctx = {'cwd': '/tmp/sbdk-test'}
        ctx.update(BASE_CTX)
        if conf & IMAGE:
            ctx['image_id'] = '1234567890ab'
        if conf & DIR:
            ctx['project_dir'] = 'prj'
            os.makedirs('/tmp/sbdk-test/prj')
            os.chdir('/tmp/sbdk-test')

        p = Project(ctx)

        try:
            for name, cmd in CMDS.iteritems():
                satisfied = (conf & cmd['depend']) == cmd['depend']
                try:
                    cmd['cmd'](p)
                    assert satisfied, "The command {} should fail as it's conditions are not satisfied".format(name)
                except SbdkError, e:
                    if satisfied:
                        raise
                    else:
                        print "Ignoring expected message {} for command {}".format(e.message, name)

        finally:
            if p.project_dir and os.path.isdir(p.project_dir):
                shutil.rmtree(p.project_dir)
