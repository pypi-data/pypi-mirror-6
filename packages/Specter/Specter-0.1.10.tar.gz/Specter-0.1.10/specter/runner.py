import sys
from random import shuffle
from argparse import ArgumentParser

from coverage import coverage
from specter import _
from specter.scanner import SuiteScanner
from specter.reporting import ConsoleReporter


class SpecterRunner(object):
    DESCRIPTION = _('Specter is a spec-based testing library to help '
                    'facilitate BDD in Python.')

    def __init__(self):
        super(SpecterRunner, self).__init__()
        self.coverage = None
        self.suite_scanner = SuiteScanner()
        self.collector = ConsoleReporter()
        self.arg_parser = ArgumentParser(description=self.DESCRIPTION)
        self.setup_argparse()
        self.suites = []

    def setup_argparse(self):
        self.arg_parser.add_argument(
            '--coverage', dest='coverage', action='store_true',
            help=_('Activates coverage.py integration'))
        self.arg_parser.add_argument(
            '--search', type=str, dest='search',
            help=_('The spec suite folder path.'))
        self.arg_parser.add_argument(
            '--no-art', dest='no_art', action='store_true',
            help=_('Disables ASCII art'))
        self.arg_parser.add_argument(
            '--select-module', dest='select_module',
            help=_('Selects a module path to run. '
                   'Ex: spec.sample.TestClass'),
            default=None)
        self.arg_parser.add_argument(
            '--select-by-metadata', dest='select_meta',
            help=_('Selects tests to run by specifying a list of '
                   'key=value pairs you wish to run'),
            default=[], nargs='*')

    def generate_ascii_art(self):
        tag_line = _('Keeping the boogy man away from your code!')
        ascii_art = """
          ___
        _/ @@\\
    ~- ( \\  O/__     Specter
    ~-  \\    \\__)   ~~~~~~~~~~
    ~-  /     \\     {tag}
    ~- /      _\\
       ~~~~~~~~~
    """.format(tag=tag_line)
        return ascii_art

    def run(self, args):
        select_meta = None
        self.arguments = self.arg_parser.parse_args(args)

        if self.arguments.select_meta:
            metas = [meta.split('=') for meta in self.arguments.select_meta]
            select_meta = {meta[0]: meta[1].strip('"\'') for meta in metas}

        if not self.arguments.no_art:
            print(self.generate_ascii_art())

        if self.arguments.coverage:
            print(_(' - Running with coverage enabled - '))
            self.coverage = coverage(omit=['*/pyevents/event.py',
                                           '*/pyevents/manager.py',
                                           '*/specter/spec.py',
                                           '*/specter/expect.py',
                                           '*/specter/reporting.py',
                                           '*/specter/__init__.py'])
            self.coverage._warn_no_data = False

        self.suite_types = self.suite_scanner.scan(
            search_path=self.arguments.search,
            module_name=self.arguments.select_module)

        for suite_type in self.suite_types:
            # Start Coverage Capture
            if self.coverage:
                self.coverage.start()

            suite = suite_type()
            self.suites.append(suite)
            self.collector.add_describe(suite)
            suite.execute(select_metadata=select_meta)

            # Start Coverage Capture
            if self.coverage:
                self.coverage.stop()

        # Save coverage data if enabled
        if self.coverage:
            self.coverage.save()

        self.collector.print_summary()
        self.suite_scanner.destroy()


def activate(): #pragma: no cover
    args = sys.argv[1:]
    runner = SpecterRunner()
    runner.run(args)
    # Return error code if tests fail
    for suite in runner.suites:
        if not suite.success:
            exit(1)

if __name__ == "__main__":
    activate()
