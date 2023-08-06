import os
import nose.tools
from sbgsdk.tests.test_tools.generator import generator
from sbgsdk.tests.test_tools.comparator import comparator


def remove_txt_files():
    for name in os.listdir('.'):
        if name.endswith('.txt'):
            os.remove(name)


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
@nose.tools.raises(Exception)
def test_compare_random():
    count = 1000
    generator.generate('random_a.txt', count, 'random')
    generator.generate('random_b.txt', count, 'random')
    comparator.compare('random_a.txt', 'random_b.txt', 'random_c.txt')


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
def test_compare_same():
    count = 1000
    generator.generate('same_a.txt', count, 'same', 45)
    generator.generate('same_b.txt', count, 'same', 45)
    comparator.compare('same_a.txt', 'same_b.txt', 'same_c.txt')

    f = open('same_c.txt')
    first_line = f.readline()
    count2 = int(first_line.rstrip())
    nose.tools.assert_equals(count, count2)

    line_count = 0
    for line in f:
        integer_num = int(line.rstrip(), 16)
        assert(integer_num == 45)
        line_count += 1
    nose.tools.assert_equals(line_count, count)

    f.close()


@nose.tools.with_setup(remove_txt_files, remove_txt_files)
@nose.tools.raises(Exception)
def test_compare_same_diff_length():
    generator.generate('same_a.txt', 1000, 'same', 45)
    generator.generate('same_b.txt', 1001, 'same', 45)
    comparator.compare('same_a.txt', 'same_b.txt', 'same_c.txt')
