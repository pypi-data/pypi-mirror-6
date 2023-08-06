import csv
import argparse
import json
import mock

from timermiddleware import TimerMiddleware
from collections import defaultdict

def count_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Count number of expensive calls (mongo, markdown, etc) for a standard page.\n'
                    'Currently its a _discuss URL with a few posts on it.  This exercises core logic\n'
                    '(project & tool lookup, security, discussion thread, main template, etc) but\n'
                    'intentionally avoids most tool-specific code.')
    parser.add_argument('--verbose', '-v', action='store_true', default=False,
                        help='Show call details.  Note that Timers with debug_each_call=False (like ming\'s Cursor.next) are not displayed in verbose mode (but they are counted).')
    parser.add_argument('--debug-output', action='store_true', default=False,
                        help='Save output returned from count methods as local files')
    parser.add_argument(
        '--data-file', default='call_counts.csv', type=argparse.FileType('a'),
        help='CSV file that is appended to')
    parser.add_argument('--id', default='',
                        help='An identifier for this run.  Examples:\n'
                             '`git rev-parse --short HEAD` for current hash\n'
                             '`git log -1 --oneline` for hash + message')
    return parser.parse_args()


class CountCase(object):
    """This class is used for defining a CountCase"""
    def setUp(self):
        pass

    def tearDown(self):
        pass


class CountRunner(object):
    """This class is responsible for running a CountCase"""
    countMethodPrefix = 'count'

    def __init__(self, args):
        self.args = args
        self.results = []
        self.output = []

    def __call__(self, cases):
        self.load(cases)
        self.display()

    def load(self, cases):
        if cases:
            self.run(cases[0])
            self.load(cases[1:])

    def display(self):
        print json.dumps(self.results)

    def count_calls(self, output, func):
        calls = defaultdict(int)
        for call in output:
            key = call[0:call.find(' ')]
            calls[key] += 1
        calls['func'] = func
        if self.args.id:
            calls['id'] = self.args.id
        return calls

    def tmw_listener(self, _input):
        self.output.append(_input)

    def run(self, case):
        self.output = []
        with mock.patch('timermiddleware.log.isEnabledFor', return_value=True):

            instance = case()
            def _call(counter):
                call_key = '{}.{}'.format(case.__name__ ,counter)
                instance.setUp()
                TimerMiddleware.register_listener(self.tmw_listener)
                output = getattr(instance, counter)()
                if self.args.debug_output:
                    debug_filename = '{}.out'.format(call_key)
                    with open(debug_filename, 'w') as out:
                        out.write(output)

                self.results.append(self.count_calls(self.output, call_key))
                TimerMiddleware.unregister_listener(self.tmw_listener)
                instance.tearDown()

            map(_call, self.get_counters(case))

            if self.args.verbose:
                print '\n'.join(self.output)
            self.write_csv()

    def write_csv(self):
        cols = sorted(self.results[0].keys())

        out = csv.DictWriter(self.args.data_file, cols)
        if self.args.data_file.tell() == 0:
            out.writeheader()

        for row in self.results:
            out.writerow(row)
        self.args.data_file.close()

    def get_counters(self, case):
        def is_count_method(attrname):
            return (attrname.startswith(CountRunner.countMethodPrefix) and
                    callable(getattr(case, attrname)))
        return list(filter(is_count_method, dir(case)))


