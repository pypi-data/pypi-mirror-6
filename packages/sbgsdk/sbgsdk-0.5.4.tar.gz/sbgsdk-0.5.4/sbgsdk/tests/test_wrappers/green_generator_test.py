import os
import nose.tools
from sbgsdk.tests.test_wrappers.green_generator import GeneratorWrapper
from sbgsdk.tests.common import cleanup


def remove_temp_files():
    for name in os.listdir('.'):
        if name.endswith('.txt') or name.endswith('.meta'):
            os.remove(name)


cleanup = nose.tools.with_setup(remove_temp_files, remove_temp_files)


@cleanup
def _check_file(filename, count, condition):
    f = open(filename)
    first_line = f.readline()
    count2 = int(first_line.rstrip())
    nose.tools.assert_equals(count, count2)

    line_count = 0
    for line in f:
        integer_num = int(line.rstrip(), 16)
        assert(condition(integer_num))
        line_count += 1
    nose.tools.assert_equals(line_count, count)

    f.close()


@cleanup
def test_generator_random():
    w = GeneratorWrapper(
        inputs={},
        params={
            'number_of_files': 1,
            'numbers_per_file': 1000,
            'template_number': 3,
            'numbers_to_generate': 'random'
        }
    )

    w.test()

    filename = w.outputs.output[0].file
    count = w.params['numbers_per_file']
    check = lambda x: 0 <= x < 256
    _check_file(filename, count, check)


@cleanup
def test_generator_same():
    w = GeneratorWrapper(
        inputs={},
        params={
            'number_of_files': 1,
            'numbers_per_file': 1000,
            'template_number': 44,
            'numbers_to_generate': 'same'
        }
    )

    count = w.params['numbers_per_file']

    w.test()

    filename = w.outputs.output[0].file
    count = w.params['numbers_per_file']
    check = lambda x: x == 44
    _check_file(filename, count, check)


@cleanup
def test_generator_two_files():
    w = GeneratorWrapper(
        inputs={},
        params={
            'number_of_files': 2,
            'numbers_per_file': 1000,
            'template_number': 3,
            'numbers_to_generate': 'random'
        }
    )

    count = w.params['numbers_per_file']

    w.test()

    filename0 = w.outputs.output[0].file
    count0 = w.params['numbers_per_file']
    check0 = lambda x: 0 <= x < 256
    _check_file(filename0, count0, check0)

    filename1 = w.outputs.output[1].file
    count1 = w.params['numbers_per_file']
    check1 = lambda x: 0 <= x < 256
    _check_file(filename1, count1, check1)
