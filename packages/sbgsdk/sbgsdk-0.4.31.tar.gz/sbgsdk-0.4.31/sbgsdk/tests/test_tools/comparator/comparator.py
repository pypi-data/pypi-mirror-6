import shutil


def compare(filename_a, filename_b, filename_out):
    """ compares two hex list files and if same -> outputs same file, else error"""

    with open(filename_a, 'r') as fa, open(filename_b, 'r') as fb:
        count_a = int(fa.readline())
        count_b = int(fb.readline())

        assert count_a == count_b, "Different sizes: count_a(%d) != count_b(%d)" % (count_a, count_b)

        for i in xrange(count_a):
            a = int(fa.readline(), 16)
            b = int(fb.readline(), 16)
            assert a == b, "Different numbers on line#%d: a=%d != b=%d" % (i, a, b)

    shutil.copyfile(filename_a, filename_out)
