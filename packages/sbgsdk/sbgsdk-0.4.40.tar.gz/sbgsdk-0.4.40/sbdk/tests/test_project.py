__author__ = 'luka'
import tempfile
from nose.tools import *

from sbdk.error import SbdkError
from sbdk.project import destination, sanitize_project_name


def test_destination():
    cwd = tempfile.mkdtemp()
    empty = destination(cwd, '')
    eq_(cwd, empty, "Destination should stay unchanged")


def test_sanitize_valid():
    for valid in 'valid', 'val1d', 'va_lid':
        result = sanitize_project_name(valid)
        eq_(valid, result, "Valid name should stay unchanged")


def test_sanitize_minus():
    minus = sanitize_project_name('has-minus')
    eq_(minus, 'has_minus', "Minus should change to underscore")


@raises(SbdkError)
def test_sanitize_keyword():
    keyword = sanitize_project_name('while')


@raises(SbdkError)
def test_sanitize_pattern():
    illegal = sanitize_project_name('1asd')
