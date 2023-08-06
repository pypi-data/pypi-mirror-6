import os
import nose.tools
from sbgsdk.tests.test_tools.generator import generator
from sbgsdk.tests.test_tools.adder import adder


def remove_txt_files():
    for name in os.listdir('.'):
        if name.endswith('.txt'):
            os.remove(name)


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
def test_add_same():
    count = 1000
    generator.generate('same_a.txt', count, 'same', 22)
    generator.generate('same_b.txt', count, 'same', 33)
    adder.add('same_a.txt', 'same_b.txt', 'same_c.txt')

    f = open('same_c.txt')
    first_line = f.readline()
    count2 = int(first_line.rstrip())
    nose.tools.assert_equals(count, count2)

    line_count = 0
    for line in f:
        integer_num = int(line.rstrip(), 16)
        assert(integer_num == 55)
        line_count += 1
    nose.tools.assert_equals(line_count, count)

    f.close()


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
@nose.tools.raises(Exception)
def test_add_diff_length():
    generator.generate('same_a.txt', 1000, 'same', 45)
    generator.generate('same_b.txt', 1001, 'same', 45)
    adder.add('same_a.txt', 'same_b.txt', 'same_c.txt')


def test_split_deltas():
    res = adder._split_deltas(12, 3)
    assert res[0] == 4
    assert res[1] == 4
    assert res[2] == 4

    res = adder._split_deltas(11, 3)
    assert res[0] == 4
    assert res[1] == 4
    assert res[2] == 3

    res = adder._split_deltas(10, 3)
    assert res[0] == 4
    assert res[1] == 4
    assert res[2] == 2

    res = adder._split_deltas(9, 3)
    assert res[0] == 3
    assert res[1] == 3
    assert res[2] == 3

    res = adder._split_deltas(3, 3)
    assert res[0] == 1
    assert res[1] == 1
    assert res[2] == 1


@nose.tools.raises(ValueError)
def test_split_deltas_e1():
    adder._split_deltas(12, 0)


@nose.tools.raises(ValueError)
def test_split_deltas_e2():
    adder._split_deltas(12, -1)


@nose.tools.raises(ValueError)
def test_split_deltas_e3():
    adder._split_deltas(12, 13)


@nose.tools.raises(ValueError)
def test_split_deltas_e4():
    adder._split_deltas(0, 0)


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
def test_split():
    generator.generate('numbers.txt', 11, 'random')
    adder.split('numbers.txt', 3)
    assert_size(adder.get_part_name('numbers.txt', 0), 4)
    assert_size(adder.get_part_name('numbers.txt', 1), 4)
    assert_size(adder.get_part_name('numbers.txt', 2), 3)


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
def test_unsplit():
    generator.generate('numbers.txt', 11, 'random')
    file_names = adder.split('numbers.txt', 3)
    adder.unsplit('out.txt', file_names)
    assert_size('out.txt', 11)


def assert_size(filename, n):
    fa = open(filename, 'rb+')
    total_count = int(fa.readline())
    assert total_count == n
    fa.close()

