from sbgsdk.errors import *


class JobException(Exception):
    def __json__(self):
        return {'$$type': 'error', 'message': self.message or str(self)}

    @classmethod
    def from_dict(cls, d):
        return cls(d.get('message', 'Job error'))


################################################# PROTOCOL EXCEPTIONS ##################################################
class ProtocolException(JobException):
    pass


class NoWrapperIdException(ProtocolException):
    pass


class NoResourcesException(ProtocolException):
    pass


class NoSuchMethodError(ProtocolException):
    pass


class NotAJobError(ProtocolException):
    pass


################################################# VALIDATION EXCEPTIONS ################################################
class ValidationException(JobException):
    pass


class InputsValidationException(ValidationException):
    pass


class ParamsValidationException(ValidationException):
    pass


########################################################################################################################
__exit_codes = {
    InputsValidationException: INPUTS_VALIDATION_ERROR,
    ParamsValidationException: PARAMS_VALIDATION_ERROR,
    JobException: JOB_ERROR,
    NoWrapperIdException: NO_WRAPPER_ID_ERROR,
    NotAJobError: NOT_A_JOB_ERROR,
    NoSuchMethodError: NO_SUCH_METHOD_ERROR,
    NoResourcesException: NO_RESOURCES_ERROR
}


def exit_code_for_exception(exception):
    return __exit_codes.get(exception.__class__, EXIT_CODE_MAPPING_ERROR)
