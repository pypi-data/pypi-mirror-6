__author__ = 'sinisa'
from sbgsdk import define


class InputWrapper(define.Wrapper):
    for_each = ['inputA', 'params.group_by']

    class Outputs(define.Outputs):
        output = define.output(
            list=True,
            name="output",
            description="",
            file_types=[],
        )

    class Params(define.Params):
        path = define.string(
            name = "Input files",
            description = "Input files",
            list=True,
            )

    def execute(self):
        for param in self.params.path:
            self.outputs.output.add_file(param)._load_meta()
