import filecmp


def assert_files_identical(file1, file2):
    if not filecmp.cmp(file1, file2, shallow=False):
        raise AssertionError('Files %s and %s do not match' % (file1, file2))

