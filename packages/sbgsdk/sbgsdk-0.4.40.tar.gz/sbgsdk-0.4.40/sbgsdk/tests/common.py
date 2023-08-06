import os
import shutil
import nose


from sbgsdk import Process
from sbgsdk.tests.test_wrappers.red_adder import RedAdder

RED_ADDER_ID = '.'.join([RedAdder.__module__, RedAdder.__name__])


def remove_temp_files():
    prefixes = ['process_', 'random_a_', 'random_b_', 'output_']
    suffixes = ['.txt']
    temp_files = ['__out__.json', '__exec__.log']
    wrapper_names = 'BlueComparator', 'GeneratorWrapper', 'RedAdder'
    for filename in os.listdir('.'):
        if any(map(filename.startswith, prefixes)) or any(map(filename.endswith, suffixes)):
            temp_files.append(filename)
    for filename in temp_files:
        if os.path.isfile(filename):
            os.remove(filename)
    for dirname in os.listdir('.'):
        if os.path.isdir(dirname) and any(map(dirname.startswith, ['test_%s_' % wrp for wrp in wrapper_names])):
            shutil.rmtree(dirname)


cleanup = nose.tools.with_setup(remove_temp_files, remove_temp_files)


def run_cli(*args):
    p = Process('python', '-m', 'sbgsdk.cli', *args)
    p.run()
    return p

