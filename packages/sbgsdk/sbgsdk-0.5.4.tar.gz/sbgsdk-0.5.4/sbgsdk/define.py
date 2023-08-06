from sbgsdk import schema as _
from wrapper import Wrapper

Inputs = _.Inputs
input = _.IOAttr

Outputs = _.Outputs
output = _.IOAttr

Params = _.Params
integer = _.IntAttr
boolean = _.BoolAttr
enum = _.EnumAttr
real = _.RealAttr
string = _.StringAttr
struct = _.StructAttr
__wrapper__ = Wrapper
