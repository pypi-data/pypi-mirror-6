import os

from {project.name}.grep.wrapper import GrepWrapper


def in_files(*args):
    return [os.path.join(os.path.dirname(__file__), p) for p in args]


def test_grep_wrapper():
    out = GrepWrapper({{'in_file': in_files('test/words.txt')}}, {{'pattern': 'three', 'suffix': 'three'}}).test().out_file
    assert out.endswith('words.three.txt')
    with open(out) as fp:
        lines = fp.readlines()
    assert len(lines) == 1
    assert 'three' in lines[0]
