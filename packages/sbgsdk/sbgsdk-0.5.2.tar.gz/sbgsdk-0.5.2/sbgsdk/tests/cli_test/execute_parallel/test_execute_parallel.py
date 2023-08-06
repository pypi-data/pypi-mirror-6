import os
import json

from sbgsdk.tests.common import run_cli, cleanup, RED_ADDER_ID


def test_setup():
    os.chdir(os.path.dirname(__file__))

@cleanup
def test_execute_parallel():
    run_cli('run', '-i', 'input_parallel.json', '-o', 'output_parallel.json')
    s = json.load(open('output_parallel.json'))
    assert s['wrapper_id'] == RED_ADDER_ID
    assert s['$$type'] == 'job'
    assert s['args']['$method'] == 'split'


@cleanup
def test_execute_split():
    run_cli('run', '-i', 'input_split.json', '-o', 'output_split.json')
    s = json.load(open('output_split.json'))
    assert s['$$type'] == 'job'
    assert s['args']['$method'] == 'unsplit'
    assert len(s['args']['files']) == 10


@cleanup
def test_execute_add():
    run_cli('run', '-i', 'input_add.json', '-o', 'output_add.json')
    s = json.load(open('output_add.json'))
    assert isinstance(s, basestring) and s.endswith('.txt'), 'Unexpected output: %s' % s


@cleanup
def test_execute_unsplit():
    run_cli('run', '-i', 'input_unsplit.json', '-o', 'output_unsplit.json')
    s = json.load(open('output_unsplit.json'))
    assert s['c'].endswith('/output_parallel.txt'), 'Unexpected output c: %s' % s['c']
    assert os.path.isfile(s['c'])

