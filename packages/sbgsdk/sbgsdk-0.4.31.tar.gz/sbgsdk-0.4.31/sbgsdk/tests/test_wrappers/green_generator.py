import os

from sbgsdk import define
from sbgsdk.tests.test_tools.generator import generator
from sbgsdk.sgw import ScatterGatherWrapper


class GeneratorWrapper(ScatterGatherWrapper):
    class Outputs(define.Outputs):
        output = define.output(
            list=True,
            name="output",
            description="Text file containing a list of hex characters",
            #file_types=['text'],
        )

    class Params(define.Params):
        number_of_files = define.integer(required=True, description='How many files to generate, Master?', default=1)
        numbers_per_file = define.integer(required=True, description='How many numbers per file, Master?', default=1024)
        template_number = define.integer(required=True, description='What number to write in files, Master?', default=0)
        numbers_to_generate = define.enum(
            required=True,
            values=['same', 'random'],
            name="Numbers To Generate",
            description="Type of numbers to generate (same or random). [default: random]",
            default="random",
        )

    def execute(self):
        outputs, params = self.outputs, self.params
        for i in range(0, params.number_of_files):
            filename = 'hex' + str(i) + '.txt'
            generator.generate(filename, params.numbers_per_file, params.numbers_to_generate, params.template_number)
            outputs.output.add_file(filename).meta = outputs.output.make_metadata(file_type='text', sample='s'+str(i))

    def split(self):
        return [{'job_index': x} for x in xrange(self.params.number_of_files)]

    def work(self, job):
        assert 'job_index' in job, str(job)
        p = self.params
        file_path = os.path.abspath('hex' + str(job['job_index']) + '.txt')
        generator.generate(file_path, p.numbers_per_file, p.numbers_to_generate, p.template_number)
        return file_path

    def merge(self, job_results):
        for result in job_results:
            out = self.outputs.output.add_file(result)
            out.meta = {"file_type": 'text', "sample": os.path.basename(result)}
