import logging
from multiprocessing import Pipe


class JobManager(object):
    def __init__(self, job_class, logger=None, **kwargs):
        """ Job manager

        :param job_class: Job class
        :param logger: logger
        :param kwargs: kwargs
        """
        if not logger:
            logger = logging.getLogger()

        self.logger = logger

        self.job_class = job_class
        self.job_list = list()

    @property
    def job_count(self):
        """Job count
        :return: Job count
        """
        return len(self.job_list)

    def start(self, job_count, seeds=None, **kwargs):
        """Start Job

        :param job_count: number of job
        :param kwargs: job class kwargs
        """
        for i in xrange(job_count):
            seed = None
            if seeds:
                try:
                    seed = seeds.pop()
                except IndexError:
                    pass

            kwargs['seed'] = seed

            parent_pipe, child_pipe = Pipe()
            w = self.job_class(pipe=child_pipe, kwargs=kwargs)
            w.start()
            self.job_list.append((parent_pipe, w))

    def results(self):
        """Iterate over result
        yield job, job.recv()
        """
        for pipe, job in self.job_list:
            job.join()
            yield job, pipe.recv()

    def recv_result(self):
        """Iterate over job recv
        yield job.recv()
        """
        for pipe, _ in self.job_list:
            yield pipe.recv()
