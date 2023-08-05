import os
import json

from sbgsdk import errors
from sbgsdk.process import process_fails
from sbgsdk.tests.common import run_cli, cleanup, RED_ADDER_ID


def test_setup():
    os.chdir(os.path.dirname(__file__))


@cleanup
@process_fails(exit_code=errors.NOT_A_JOB_ERROR)
def test_run_not_a_job():
    run_cli('run', '-i', 'input_not_a_job.json')


@cleanup
@process_fails(exit_code=errors.NO_WRAPPER_ID_ERROR)
def test_run_no_wrapper_id():
    run_cli('run', '-i', 'input_no_wrapper_id.json')


@cleanup
@process_fails(exit_code=errors.NO_RESOURCES_ERROR)
def test_run_no_resources():
    run_cli('run', '-i', 'input_no_resources.json')
    s = json.load(open('__out__.json'))
    assert s['wrapper_id'] == RED_ADDER_ID
    assert s['$$type'] == 'job'
    assert s['args']['$method'] == 'execute'


@cleanup
@process_fails(exit_code=errors.INPUTS_VALIDATION_ERROR)
def test_run_required_input_missing():
    run_cli('run', '-i', 'input_required_input_missing.json')


@cleanup
@process_fails(exit_code=errors.PARAMS_VALIDATION_ERROR)
def test_run_invalid_param():
    run_cli('run', '-i', 'input_invalid_param.json')


@cleanup
def test_run():
    run_cli('run', '-i', 'input.json')
    s = json.load(open('__out__.json'))
    assert s['wrapper_id'] == RED_ADDER_ID
    assert s['$$type'] == 'job'
    assert s['args']['$method'] == 'execute'

