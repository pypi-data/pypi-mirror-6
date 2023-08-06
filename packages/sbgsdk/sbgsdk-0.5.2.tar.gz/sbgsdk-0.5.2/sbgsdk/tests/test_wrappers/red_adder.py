from uuid import uuid4
import os
from sbgsdk import define, require
from sbgsdk.tests.test_tools.adder import adder


@require(200, cpu=require.CPU_NEGLIGIBLE)
class RedAdder(define.Wrapper):
    class Inputs(define.Inputs):
        a = define.input(required=True, list=True)
        b = define.input(required=True, list=True)

    class Params(define.Params):
        n = define.integer(default=1, min=1)

    class Outputs(define.Outputs):
        output = define.output(list=True)

    def _out_file_name(self, sample):
        return 'sum_of_'+sample+'.txt'

    def execute(self):
        assert self.get_allocated_memory('MB') == 200, 'expected resources mismatch (%s, 200)' % self.resources.mem_mb
        if self.params.n > 1:
            return self.execute_parallel()

        by_sample_a = {}
        for i in xrange(len(self.inputs.a)):
            key = self.inputs.a[i].meta['sample']
            by_sample_a[key] = self.inputs.a[i]

        by_sample_b = {}
        for i in xrange(len(self.inputs.b)):
            key = self.inputs.b[i].meta['sample']
            by_sample_b[key] = self.inputs.b[i]

        for k in by_sample_a.keys():
            adder.add(by_sample_a[k], by_sample_b[k], self._out_file_name(k))
            out = self.outputs.output.add_file(self._out_file_name(k))
            out.meta = {'sample': k}

    def execute_parallel(self):
        return self.job('split', requirements=require(300, cpu=require.CPU_SINGLE))

    def split(self):
        assert self.get_allocated_memory('MB') == 300, 'expected resources mismatch (%s, 300)' % self.resources.mem_mb
        a_files = map(os.path.abspath, adder.split(self.inputs.a[0], self.params.n))
        b_files = map(os.path.abspath, adder.split(self.inputs.b[0], self.params.n))
        return self.job('unsplit',
                        {'files': [self.job('add', {'files': [a, b]}) for a, b in zip(a_files, b_files)]},
                        requirements=require(mem_mb=400, cpu=require.CPU_ALL))

    @require(500)
    def add(self, files):
        assert self.get_allocated_memory('MB') == 500, 'expected resources mismatch (%s, 500)' % self.resources.mem_mb
        temp_out = str(uuid4()) + ".txt"
        adder.add(files[0], files[1], temp_out)
        return os.path.abspath(temp_out)

    def unsplit(self, files):
        adder.unsplit(self._out_file_name(), files)
        self.outputs.output.add_file(self._out_file_name())