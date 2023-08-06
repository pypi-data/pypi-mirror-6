from nose.tools import *

import sbdk.docker.runner as runner


def test_shell_join():
    result = runner.shell_join(['a', 'b'])
    eq_(result, 'a b', 'Bad simple escape: %s' % result)

    result = runner.shell_join(['a', 'b c'])
    eq_(result, "a 'b c'", 'Bad whitespace escape: %s' % result)

    result = runner.shell_join(['a', 'b"c'])
    eq_(result, "a 'b\"c'", 'Bad double quote escape: %s' % result)

    #result = self.runner.shell_escape('a', "b'c")
    #eq_(result, "a b\\'c", 'Bad single quote escape: %s' % result)


def test_multi_command():
    eq_(runner.multi_command('a', 'b'), ['/bin/sh', '-c', 'a && b'], 'Bad simple join')
