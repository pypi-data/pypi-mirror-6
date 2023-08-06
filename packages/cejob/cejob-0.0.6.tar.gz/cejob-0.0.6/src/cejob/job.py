import time
import logging
from multiprocessing import Process


class Job(Process):
    def __init__(self, pipe, logger=None, **kwargs):
        """
        :param pipe: Pipe
        :param logger: Logger
        :param args: args
        :param kwargs: kwargs
        """
        super(Job, self).__init__(**kwargs)

        if not logger:
            logger = logging.getLogger()

        self.logger = logger
        self.pipe = pipe

    def run(self):
        """ Run job_class.
        """
        self.on_init(**self._kwargs)

        start_time = time.clock()
        start_time_real = time.time()
        ret = self.on_start(**self._kwargs)
        self.elapsed_time = time.clock() - start_time
        self.elapsed_time_real = time.time() - start_time_real

        ret.update({
            'elapsed_time': self.elapsed_time,
            'elapsed_time_real': self.elapsed_time_real,
        })

        self.pipe.send(ret)

    def on_start(self, **kwargs):
        """ On start callback

        :param kwargs:Job kwargs
        :raise NotImplementedError:
        """
        raise NotImplementedError

    def on_init(self, **kwargs):
        """ On init callback

        :param kwargs:
        """
        pass