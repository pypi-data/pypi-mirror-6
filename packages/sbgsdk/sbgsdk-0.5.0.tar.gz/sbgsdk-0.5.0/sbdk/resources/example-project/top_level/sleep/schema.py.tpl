from sbgsdk import define


class Inputs(define.Inputs):
    a = define.input()


class Outputs(define.Outputs):
    a = define.output()


class Params(define.Params):
    seconds = define.integer(default=1)
