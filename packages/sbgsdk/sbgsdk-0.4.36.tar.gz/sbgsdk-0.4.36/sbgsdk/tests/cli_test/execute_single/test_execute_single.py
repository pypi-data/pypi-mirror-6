import os
import json

from sbgsdk import errors
from sbgsdk.process import process_fails
from sbgsdk.tests.common import run_cli, cleanup


def test_setup():
    os.chdir(os.path.dirname(__file__))


@cleanup
@process_fails(exit_code=errors.NO_SUCH_METHOD_ERROR)
def test_execute_no_such_method():
    run_cli('run', '-i', 'input_no_such_method.json')


@cleanup
@process_fails(exit_code=errors.NO_RESOURCES_ERROR)
def test_execute_no_resources():
    run_cli('run', '-i', 'input_execute_no_resources.json')


@cleanup
def test_execute_single():
    run_cli('run', '-i', 'input_single.json', '-o', 'output_single.json')
    s = json.load(open('output_single.json'))
    assert s['c'].endswith('/output_single.txt'), 'Unexpected output c: %s' % s['c']
    assert os.path.isfile(s['c'])

