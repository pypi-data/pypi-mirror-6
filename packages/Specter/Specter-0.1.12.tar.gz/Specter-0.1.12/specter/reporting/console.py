import re
import six
from specter.spec import TestEvent, DescribeEvent, DataDescribe
from specter import _
from specter.reporting import AbstractConsoleReporterPlugin


class TestStatus():
    PASS = 'passed'
    FAIL = 'failed'
    SKIP = 'skipped'
    INCOMPLETE = 'incomplete'
    ERROR = 'error'


class ConsoleColors():
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class ConsoleReporter(AbstractConsoleReporterPlugin):
    """ Temporary console reporter.
    At least until I can get a real one written.
    """
    INDENT = 2

    def __init__(self, output_docstrings=False, use_color=True):
        super(ConsoleReporter, self).__init__()
        self.use_color = use_color
        self.test_total = 0
        self.test_expects = 0
        self.passed_tests = 0
        self.skipped_tests = 0
        self.errored_tests = 0
        self.failed_tests = 0
        self.incomplete_tests = 0
        self.output_docstrings = output_docstrings

    def get_name(self):
        return 'Temporary console reporter'

    def process_arguments(self, args):
        if args.no_color:
            self.use_color = False

    def subscribe_to_describe(self, describe):
        describe.add_listener(TestEvent.COMPLETE, self.event_received)
        describe.add_listener(DescribeEvent.START, self.start_describe)

    def print_test_msg(self, msg, level, status=TestStatus.PASS):
        color = ConsoleColors.RED
        if status == TestStatus.PASS:
            color = ConsoleColors.GREEN
        elif status == TestStatus.SKIP:
            color = ConsoleColors.YELLOW
        elif status == TestStatus.INCOMPLETE:
            color = ConsoleColors.MAGENTA

        self.print_indent_msg(msg=msg, level=level, color=color)

    def print_test_args(self, kwargs, level, status=TestStatus.PASS):
        if kwargs and (status == TestStatus.ERROR or status == TestStatus.FAIL):
            msg = u''.join([u'  Parameters: ', self.pretty_print_args(kwargs)])
            self.print_test_msg(msg, level, status)

    def pretty_print_args(self, kwargs):
        if kwargs is None:
            return u'None'
        first_seen = False
        parts = []
        for k, v in six.iteritems(kwargs):
            if not first_seen:
                first_seen = True
            else:
                parts.append(', ')
            parts.append('{name} = {value}'.format(name=k, value=v))
        return u''.join(parts)

    def print_msg_list(self, msg_list, level, color=ConsoleColors.WHITE):
        for msg in msg_list:
            self.print_indent_msg(msg=msg, level=level, color=color)

    def print_indent_msg(self, msg, level=0, color=ConsoleColors.WHITE):
        indent = u' ' * self.INDENT
        msg = u'{0}{1}'.format(str(indent * level), msg)
        self.print_colored(msg=msg, color=color)

    def print_colored(self, msg, color=ConsoleColors.WHITE):
        if self.use_color:
            msg = u'\033[{color}m{msg}\033[0m'.format(color=color, msg=msg)

        print(msg.encode('utf-8'))

    def get_item_level(self, item):
        levels = 0
        parent_above = item.parent
        while parent_above is not None:
            levels += 1
            parent_above = parent_above.parent
        return levels

    def event_received(self, evt):
        test_case = evt.payload
        level = self.get_item_level(test_case)
        name = test_case.pretty_name
        if level > 0:
            name = u'\u221F {0}'.format(name)

        status = TestStatus.FAIL
        if (test_case.success and not test_case.skipped
            and not test_case.incomplete):
            status = TestStatus.PASS
        elif test_case.incomplete:
            status = TestStatus.INCOMPLETE
            name = u'{name} (incomplete)'.format(name=name)
        elif test_case.skipped:
            status = TestStatus.SKIP
            name = u'{name} (skipped): {reason}'.format(
                name=name, reason=test_case.skip_reason)
        elif test_case.error:
            status = TestStatus.ERROR

        self.print_test_msg(name, level, status)

        self.print_test_args(test_case.execute_kwargs, level, status)

        if test_case.doc and self.output_docstrings:
            self.print_indent_msg(test_case.doc, level+1, status)

        # Print error if it exists
        if test_case.error:
            for line in test_case.error:
                self.print_test_msg(line, level+2, TestStatus.FAIL)

        # Print expects
        for expect in test_case.expects:
            mark = u'\u2718'

            status = TestStatus.FAIL
            if expect.success:
                status = TestStatus.PASS
                mark = u'\u2714'

            expect_msg = u'{mark} {msg}'.format(mark=mark, msg=expect)

            self.print_test_msg(expect_msg, level+1, status=status)

            def hardcoded(param):
                result = re.match('^(\'|"|\d)', str(param)) is not None
                return result

            def print_param(value, param, indent, prefix):
                if not expect.success and not hardcoded(param):
                    msg_list = str(value).splitlines() or ['']
                    prefix = _('{0}: {1}').format(param or prefix, msg_list[0])
                    self.print_indent_msg(prefix, indent)
                    if len(msg_list) > 1:
                        self.print_msg_list(msg_list[1:], indent)

            print_param(expect.target, expect.target_src_param,
                        level + 3, 'Target')
            print_param(expect.expected, expect.expected_src_param,
                        level + 3, 'Expected')

        # Add test to totals
        self.test_total += 1
        if (test_case.success and not test_case.skipped
            and not test_case.incomplete):
            self.passed_tests += 1
        elif test_case.skipped:
            self.skipped_tests += 1
        elif test_case.incomplete:
            self.incomplete_tests += 1
        elif test_case.error:
            self.errored_tests += 1
        else:
            self.failed_tests += 1
        self.test_expects += len(test_case.expects)

    def start_describe(self, evt):
        level = self.get_item_level(evt.payload)
        name = evt.payload.name
        if level > 0:
            name = u'\u221F {0}'.format(name)
        self.print_indent_msg(name, level, color=ConsoleColors.GREEN)
        if evt.payload.doc and self.output_docstrings:
            self.print_indent_msg(evt.payload.doc, level+1)

        if isinstance(evt.payload, DataDescribe) and evt.payload.dup_count:
            self.print_indent_msg('Warning: Noticed {0} duplicate data '
                                  'set(s)'.format(evt.payload.dup_count),
                                  level+1, color=ConsoleColors.YELLOW)

    def print_summary(self):
        msg = """------- Summary --------
Pass            | {passed}
Skip            | {skipped}
Fail            | {failed}
Error           | {errored}
Incomplete      | {incomplete}
Test Total      | {total}
 - Expectations | {expects}
""".format(
            total=self.test_total, passed=self.passed_tests,
            failed=self.failed_tests, expects=self.test_expects,
            skipped=self.skipped_tests, incomplete=self.incomplete_tests,
            errored=self.errored_tests)

        success = self.failed_tests == 0

        self.print_colored('\n')
        self.print_test_msg('-'*24, 0, success)
        self.print_test_msg(msg, 0, success)
        self.print_test_msg('-'*24, 0, success)
