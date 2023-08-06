import os
import json
import unittest
from sbgsdk.tests.common import run_cli, remove_temp_files


class Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(__file__))

    def tearDown(self):
        remove_temp_files()

    def test_schema(self):
        p = run_cli('schema')
        s = json.loads(p.stdout.get_string())
        self.assertIsInstance(s, list)
        if s:
            self.assertIn('wrapper_id', s[0])

    def test_run_full(self):
        run_cli('run-full', '-i', 'input_full.json')
        s = json.load(open('__out__.json'))
        self.assertTrue(s['c'].endswith('output_parallel.txt'))
        self.assertTrue(os.path.isfile(s['c']))

    def test_execute_error(self):
        run_cli('run', '-i', 'input_error.json', '-o', 'output_error.json')
        s = json.load(open('output_error.json'))
        self.assertEqual(s['$$type'], 'error')
        self.assertIn('No such file', s['message'])


if __name__ == '__main__':
    unittest.main()