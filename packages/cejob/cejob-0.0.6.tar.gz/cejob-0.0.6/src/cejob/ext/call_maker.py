import argparse
import logging
import random
import time
import re

from cejob import JobManager
from cejob.job import Job


class CallMaker(Job):
    @staticmethod
    def file_to_callist(filename):
        """Parse file and return call list

        :param filename: File to load
        :return: Call list
        :rtype : list
        """
        import datetime

        logger = logging.getLogger(__name__)
        call_list = []

        with open(filename, 'r') as f:
            for l in f.readlines():
                l = l.strip()
                b_pos = l.find('(')

                if len(l) < 1:
                    logger.warning("Skip line.")
                    continue

                try:
                    name = l[:b_pos]
                    args = eval(l[b_pos:]) # !
                except:
                    logger.exception("Line eval fail '%s'", l)
                    continue

                call_list.append(
                    (name, args)
                )

        return call_list

    @staticmethod
    def iterate_call_list(call_list):
        """Iterate over call list

        :param call_list: Call list
        """
        for call in call_list:
            yield call[0], call[1:]

    @staticmethod
    def random_pick(call_list, infinite=False):
        """Pick random item prom call list

        :param call_list: call list
        :param infinite: Infinite call list?
        """
        tmp_call_list = list(call_list)
        while True:
            try:
                random_choice = random.choice(tmp_call_list)
                call, args = random_choice[0], random_choice[1]

                if not infinite:
                    tmp_call_list.remove(random_choice)

                yield call, args
            except IndexError:
                break

    def on_init(self, seed=None, **kwargs):
        """On init callback

        :param seed: random seed
        :param kwargs: kwargs
        """
        if not seed:
            seed = time.time() + self.pid

        random.seed(seed)
        self.seed = seed

        self.call_count = 0
        self.call_fail_count = 0
        self.on_prepare(**kwargs)

    def on_start(self, call_list, repeat_count, call_count, **kwargs):
        """On start callback

        :param call_list: Call list
        :param repeat_count: Job repeat count
        :param call_count: Job max call count
        :param kwargs: kwargs
        :return: result
        """
        on_call = self.on_call
        for i in xrange(repeat_count):
            tmp_call_count = call_count
            for call, args in self.random_pick(call_list, len(call_list) < call_count):
                cc_not_negative = tmp_call_count > -1
                if cc_not_negative and tmp_call_count == 0:
                    break
                elif cc_not_negative:
                    tmp_call_count -= 1

                self.logger.info(
                    'Call %i %s%s.',
                    i,
                    call,
                    args
                )

                try:
                    on_call(call, call_args=args)
                except Exception:
                    self.call_fail_count += 1
                    self.logger.exception(
                        'Call %i %s%s fail.',
                        i,
                        call,
                        args
                    )

                self.call_count += 1

        return {
            'call_count': self.call_count,
            'call_fail_count': self.call_fail_count,
            'seed': self.seed,
        }

    def on_call(self, call, call_args):
        """On call callback

        :param call: call name
        :param call_args: call args
        :raise NotImplemented:
        """
        raise NotImplemented

    def on_prepare(self, **kwargs):
        """On prepare callback

        :param kwargs: kwargs
        """
        pass


def callmaker_argparse(arg_parse):
    """Add some args to argparse.

    :param arg_parse: arg_parse
    """
    arg_parse.add_argument('-j', '--job', dest='job_count', action='store',
                           default=1, help='Job count (default=1)', type=int)

    arg_parse.add_argument('-r', '--repeat', dest='job_repeat_count', action='store',
                           default=1, help='Job repeat count (default=1)', type=int)

    arg_parse.add_argument('-c', '--call', dest='job_call_count', action='store',
                           default=-1, help='Job call count (default=-1, -1=all item in call list)', type=int)

    arg_parse.add_argument('-f', '--calll', dest='call_list_file', action='store',
                           help='Call list file', required=True, type=str)

    arg_parse.add_argument('-l', '--log', dest='log_file', action='store',
                           help='Log file', type=str)

    arg_parse.add_argument('-v', dest='verbose', action='store_true',
                           help='Verbose output')

    arg_parse.add_argument('-i', '--ignore', type=str, nargs='*',
                           dest='ignore_call',
                           help='comma separated regexps for ignore call name')

    arg_parse.add_argument('-s', '--seeds', type=float, nargs='*',
                           dest='seeds',
                           help='seeds')


def remove_ignore_calls(call_list, ignored, logger):
    """Remove ignore call from call list,

    :param call_list:
    :param ignored: regexp list
    :param logger: logger
    :return: call list
    """
    re_ingore = [re.compile(i) for i in ignored]
    call_list = list(call_list)
    ret = []
    for call_name, args in call_list:
        ignore = False
        for r in re_ingore:
            if r.search(call_name):
                logger.info("Call '%s' is ignore by patter '%s'.", call_name, r.pattern)
                ignore = True
                break

        if not ignore:
            ret.append((call_name, args))

    return ret


def callmaker_main(call_maker_class, args=None, logger=None, **kwargs):
    """Call maker main

    :param call_maker_class: Call maker job class
    :param args: args
    :param logger: logger
    :param kwargs: kwargs for job manager
    """
    if args is None:
        arg_parse = callmaker_argparse(argparse.ArgumentParser('Call maker'))
        args = arg_parse.parse_args()

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    if not logger:
        logging.basicConfig(
            format="%(asctime)s [%(process)d] %(levelname)s: %(message)s",
            level=log_level,


            filename=args.log_file
        )

        logger = logging.getLogger()

    def print_result(job_manager):
        call_sum = 0
        call_fail_sum = 0
        max_time = 0
        max_time_real = 0
        rs_sum = 0
        ers_sum = 0
        seeds = []

        str = "=========\n"
        str += "Processes\n"
        str += "=========\n\n"

        def safe_div(a, b, default=0):
            try:
                return a / float(b)
            except ZeroDivisionError:
                return default

        for w, r in job_manager.results():
            rs = safe_div(r['call_count'], r['elapsed_time_real'])
            ers = safe_div(r['call_fail_count'], r['elapsed_time_real'])

            elapsed = r['elapsed_time']
            elapsed_real = r['elapsed_time_real']

            rs_sum += rs
            ers_sum += ers
            call_sum += r['call_count']
            call_fail_sum += r['call_fail_count']

            success = r['call_count'] - r['call_fail_count']

            seeds.append(r['seed'])

            if elapsed > max_time:
                max_time = elapsed

            if elapsed_real > max_time_real:
                max_time_real = elapsed_real

            str += "%d\n" % w.pid
            str += "----\n"
            str += " - Time (CPU): %f\n" % elapsed
            str += " - Time elapsed: %f\n" % elapsed_real

            str += " - Requests: %d\n" % r['call_count']
            str += ' - Success: %d (%d%%)\n' % (success, safe_div(success, call_sum) * 100.0)
            str += ' - Fail: %d (%d%%)\n' % (
                r['call_fail_count'], safe_div(r['call_fail_count'], r['call_count']) * 100.0
            )

            str += " - request/s: %f\n" % rs
            str += " - error request/s: %f\n" % ers

            str += " - Seed : %f\n" % r['seed']

            str += "\n"

        success = call_sum - call_fail_sum

        str += "=======\n"
        str += "Summary\n"
        str += "=======\n"
        str += ' - Job count: %d\n' % job_manager.job_count
        str += ' - Reapeats: %d\n' % args.job_repeat_count
        str += ' - Job call count: %d\n' % (args.job_call_count if args.job_call_count > -1 else len(call_list))
        str += ' - Call list size: %d\n' % len(call_list)

        str += ' - Requests: %d\n' % call_sum
        str += ' - Success: %d (%d%%)\n' % ( success, safe_div(success, call_sum) * 100.0)
        str += ' - Fail: %d (%d%%)\n' % ( call_fail_sum, safe_div(call_fail_sum, call_sum) * 100.0)

        str += ' - Max time (CPU): %f\n' % max_time
        str += " - Max time: %f\n" % max_time_real

        str += ' - request/s: %f\n' % safe_div(call_sum, max_time_real)
        str += ' - error request/s: %f\n' % safe_div(call_fail_sum, max_time_real)

        str += ' - AVG request/s: %f\n' % safe_div(rs_sum, job_manager.job_count)
        str += ' - AVG error request/s: %f\n' % safe_div(ers_sum, job_manager.job_count)

        str += ' - Seeds: %s\n' % ('%f ' * len(seeds)) % tuple(seeds)

        print str

    call_list = CallMaker.file_to_callist(args.call_list_file)

    if args.ignore_call:
        call_list = remove_ignore_calls(call_list, args.ignore_call, logger)

    jm = JobManager(call_maker_class)
    jm.start(
        job_count=args.job_count,
        call_list=tuple(call_list),
        repeat_count=args.job_repeat_count,
        call_count=args.job_call_count,
        seeds=args.seeds,
        **kwargs
    )

    print_result(jm)