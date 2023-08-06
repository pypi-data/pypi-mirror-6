import logging
from sbgsdk.exceptions import ValidationException, JobException, ProtocolException

from sbgsdk.job import BaseJob, Job, Outputs
from sbgsdk.util import import_name
from sbgsdk.protocol import to_json


class Executor(object):
    def execute(self, job):
        pass


class Tassadar(Executor):
    def __init__(self):
        self.results = {}
        self.job_executors = {
            Job: self.exec_wrapper_job,
        }

    def execute(self, job):
        logging.debug('Job started: %s' % to_json(job))
        if job.job_id in self.results:
            return self.results[job.job_id]
        for key, val in job.args.iteritems():
            job.resolved_args[key] = self.resolve(val)
        if job.__class__ not in self.job_executors and not callable(job):
            raise NotImplementedError('Tassadar unable to run job of type %s.' % job.__class__.__name__)
        job.status = BaseJob.RUNNING
        result = job() if callable(job) else self.job_executors[job.__class__](job)
        self.results[job.job_id] = result
        job.status = BaseJob.DONE
        if isinstance(result, BaseJob):
            return self.execute(result)
        logging.debug('Job result: %s' % to_json(result))
        return result

    def exec_wrapper_job(self, job):
        cls = import_name(job.wrapper_id)
        # if not issubclass(cls, Wrapper):
        #     raise TypeError('%s is not derived from Wrapper class.' % job.wrapper_id)
        try:
            wrp = cls(inputs=job.resolved_args.pop('$inputs', {}),
                      params=job.resolved_args.pop('$params', {}),
                      context=job.context,
                      resources=job.resources)
            result = wrp(job.resolved_args.pop('$method', None), job.resolved_args)
        except (ValidationException, ProtocolException):
            raise
        except Exception as e:
            msg = get_exception_message(e)
            logging.exception('Job failed: %s', msg)
            raise JobException(msg)
        return result if result is not None else Outputs(wrp.outputs.__json__())

    def resolve(self, val):
        if isinstance(val, BaseJob):
            return self.execute(val)
        if isinstance(val, (list, tuple)):
            return [self.resolve(item) for item in val]
        if isinstance(val, dict):
            return {k: self.resolve(v) for k, v in val.iteritems()}
        return val


def get_exception_message(exception):
    return exception.message or str(exception)