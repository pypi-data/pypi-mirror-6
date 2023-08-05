import os
from sbgsdk import define, Process, require

from {project.name}.grep import schema


@require(mem_mb=100, cpu=require.CPU_SINGLE)
class GrepWrapper(define.Wrapper):
    Inputs, Outputs, Params = schema.Inputs, schema.Outputs, schema.Params

    def execute(self):
        def get_name():
            name, ext = os.path.splitext(os.path.basename(self.inputs.in_file))
            return '%s.%s%s' % (name, self.params.suffix, ext)

        out_name = get_name()
        Process('grep', self.params.pattern, self.inputs.in_file, stdout=out_name).run()
        self.outputs.out_file = out_name
        self.outputs.out_file.meta = self.inputs.in_file.make_metadata()
