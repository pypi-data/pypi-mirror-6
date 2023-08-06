import filecmp
from sbgsdk.job import Job
from sbgsdk.protocol import from_json, to_json
from sbgsdk.executor import Tassadar
from sbgsdk.tests.test_tools.generator import generator
from sbgsdk.tests.test_wrappers import RedAdder
from sbgsdk.tests.common import cleanup


@cleanup
def test_red_adder():
    inputs = {'a': ['a.txt'], 'b': ['b.txt']}
    generator.generate('a.txt')
    generator.generate('b.txt')

    job_single = Job(RedAdder, inputs=inputs, params={'n': 1})
    Tassadar().execute(job_single)

    job_multi = Job(RedAdder, inputs=inputs, params={'n': 5})
    Tassadar().execute(from_json(to_json(job_multi)))

    assert filecmp.cmp('output_parallel.txt', 'output_single.txt')