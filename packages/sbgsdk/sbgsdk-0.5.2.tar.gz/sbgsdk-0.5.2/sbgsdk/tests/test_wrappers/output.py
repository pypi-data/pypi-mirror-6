__author__ = 'sinisa'

from sbgsdk import define
import logging

class OutputWrapper(define.Wrapper):
    for_each = ['inputA', 'params.group_by']

    class Inputs(define.Inputs):
        input = define.input(
            list=True,
            name="input",
            description="",
            file_types=[],
        )

    class Params(define.Params):
        path = define.string(
            name = "Output directory",
            description = "Output directory.",
        )

    def execute(self):
        for input in self.inputs.input:
            logging.info(input)