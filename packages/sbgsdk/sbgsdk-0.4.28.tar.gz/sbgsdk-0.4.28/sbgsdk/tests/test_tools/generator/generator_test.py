import os
import nose
from nose.tools import assert_equals, raises
from sbgsdk.tests.test_tools.generator import generator


def remove_txt_files():
    for name in os.listdir('.'):
        if name.endswith('.txt'):
            os.remove(name)


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
def test_generator_random():
    count = 1000
    generator.generate('random.txt', count, 'random')
    f = open('random.txt')
    first_line = f.readline()
    count2 = int(first_line.rstrip())
    assert_equals(count, count2)

    line_count = 0
    for line in f:
        integer_num = int(line.rstrip(), 16)
        assert(0 <= integer_num < 256)
        line_count += 1
    assert_equals(line_count,count)

    f.close()


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
def test_generator_ones():
    count = 1000
    generator.generate('ones.txt', count, 'same', 1)
    f = open('ones.txt')
    first_line = f.readline()
    count2 = int(first_line.rstrip())
    assert_equals(count, count2)

    line_count = 0
    for line in f:
        num_ones = int(line.rstrip(), 16)
        assert(num_ones == 1)
        line_count += 1
    assert_equals(line_count, count)

    f.close()


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
def test_generator_zeros():
    count = 1000
    generator.generate('zeros.txt', count, 'same', 0)
    f = open('zeros.txt')
    first_line = f.readline()
    count2 = int(first_line.rstrip())
    assert_equals(count, count2)

    line_count = 0
    for line in f:
        num_ones = int(line.rstrip(), 16)
        assert(num_ones == 0)
        line_count += 1
    assert_equals(line_count, count)

    f.close()


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
@raises(ValueError)
def test_generator_wrong_count():
    count = -5
    generator.generate('zeros.txt', count, 'same', 0)


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
@raises(ValueError)
def test_generator_wrong_type():
    count = 1000
    generator.generate('zeros.txt', count, 'batman')
