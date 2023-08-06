import uuid
from sbgsdk import define
from sbgsdk.spw import SimpleParallelWrapper
from sbgsdk.tests.test_tools.comparator import comparator


class BlueComparator(SimpleParallelWrapper):
    for_each = ['inputA', 'params.group_by']

    class Inputs(define.Inputs):
        inputA = define.input(
            list=True,
            name="hex file A",
            description="Text file containing a list of hex characters",
            file_types=['text'],
        )

    class Outputs(define.Outputs):
        output = define.output(
            list=True,
            name="output",
            description="Text file containing a list of hex characters",
            file_types=['text'],
        )

    class Params(define.Params):
        group_by = define.enum(['sample', 'library', 'platform_unit', 'chunk', None])

    def execute(self):
        inputs, outputs = self.inputs, self.outputs
        filename = str(uuid.uuid4()) + '.txt'
        assert len(inputs.inputA) == 2, 'input len = %s' % len(inputs.inputA)
        comparator.compare(inputs.inputA[0], inputs.inputA[1], filename)
        outputs.output.add_file(filename).meta = inputs.inputA.make_metadata(file_type='text')