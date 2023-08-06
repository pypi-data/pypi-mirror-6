from sbgsdk import define


class Inputs(define.Inputs):
    in_file = define.input(required=True)


class Outputs(define.Outputs):
    out_file = define.output()


class Params(define.Params):
    pattern = define.string()
    suffix = define.string(default='filtered')
