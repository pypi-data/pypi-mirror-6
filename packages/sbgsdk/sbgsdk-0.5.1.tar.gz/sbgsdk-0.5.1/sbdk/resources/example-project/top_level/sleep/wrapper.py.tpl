import time
from sbgsdk import define, require

from {project.name}.sleep import schema


@require(mem_mb=100, cpu=require.CPU_NEGLIGIBLE)
class SleepWrapper(define.Wrapper):
    Inputs, Outputs, Params = schema.Inputs, schema.Outputs, schema.Params

    def execute(self):
        time.sleep(self.params.seconds)
        self.outputs.a = self.inputs.a
