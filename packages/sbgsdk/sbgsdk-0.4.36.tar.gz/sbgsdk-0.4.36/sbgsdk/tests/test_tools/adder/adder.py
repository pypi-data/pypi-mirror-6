import os

def add(filename_a, filename_b, filename_out):
    """ compares two hex list files and if same -> outputs same file, else error"""
    with open(filename_a, 'r') as fa, open(filename_b, 'r') as fb:
        count_a = int(fa.readline())
        count_b = int(fb.readline())
        assert count_a == count_b, "Different sizes: count_a(%d) != count_b(%d)" % (count_a, count_b)
        with open(filename_out, 'w') as fc:
            fc.write(str(count_a)+'\n')
            for i in xrange(count_a):
                a = int(fa.readline(), 16)
                b = int(fb.readline(), 16)
                number = hex((a+b) % 256)
                fc.write(number+'\n')


def _split_deltas(count, n):
    if count <= 0:
        raise ValueError("count must be positive! count=%s" % count)
    if n <= 0:
        raise ValueError("n must be positive! n=%s" % n)
    if count < n:
        raise ValueError("count cannot be less than n! count=%s, n=%s" % (count, n))

    delta = count / n
    if count % n != 0:
        delta += 1

    lst = []
    while count > 0:
        if delta < count:
            lst.append(delta)
            count -= delta
        else:
            lst.append(count)
            count = 0
    return lst


def get_part_name(filename, i):
    base, ext = os.path.splitext(filename)
    return base + "_" + str(i) + ext


def split(filename, n):
    """ split files into n new files """

    with open(filename, 'r') as fa:
        total_count = int(fa.readline())
        part_counts = _split_deltas(total_count, n)
        file_names = []
        for i, part_count in enumerate(part_counts):
            part_name = get_part_name(filename, i)
            with open(part_name, 'w') as file_part:
                file_names.append(part_name)
                file_part.write(str(part_count) + '\n')
                for j in xrange(part_count):
                    file_part.write(fa.readline())
    return file_names


def unsplit(outfile, file_names):
    """merge list of files into new file"""

    total_size = 0
    # get total size from first lines
    for file_name in file_names:
        with open(file_name, 'r') as fh:
            total_size += int(fh.readline())

    # write numbers from partial files into outfile
    with open(outfile, 'w') as out:
        out.write(str(total_size) + '\n')  # write total num of lines
        for file_name in file_names:
            with open(file_name, 'r') as fh:
                size = int(fh.readline())
                for x in xrange(size):
                    out.write(fh.readline())

    return outfile

