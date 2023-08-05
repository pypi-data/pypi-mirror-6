import inspect
import itertools
import sys

from time import time
from types import FunctionType, MethodType
from pyevents.manager import EventDispatcher
from pyevents.event import Event
from specter.util import (get_real_last_traceback, convert_camelcase,
                          find_by_metadata, extract_metadata,
                          children_with_tests_with_metadata)


class TimedObject(object):
    def __init__(self):
        super(TimedObject, self).__init__()
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.start_time = time()

    def stop(self):
        self.end_time = time()

    @property
    def elapsed_time(self):
        elapsed = self.end_time - self.start_time
        return elapsed if elapsed >= 0 else 0


class CaseWrapper(TimedObject):
    def __init__(self, case_func, parent, execute_kwargs=None, metadata={}):
        super(CaseWrapper, self).__init__()
        self.case_func = case_func
        self.expects = []
        self.parent = parent
        self.failed = None
        self.error = None
        self.skipped = False
        self.incomplete = False
        self.skip_reason = None
        self.execute_kwargs = execute_kwargs
        self.metadata = metadata

    def execute(self, context=None):
        kwargs = {}
        if self.execute_kwargs:
            kwargs.update(self.execute_kwargs)

        self.start()
        try:
            MethodType(self.case_func, context or self)(**kwargs)
        except TestIncompleteException:
            self.incomplete = True
        except TestSkippedException as e:
            self.skipped = True
            self.skip_reason = e.reason if type(e.reason) is str else ''
        except FailedRequireException:
            pass
        except Exception as e:
            self.error = get_real_last_traceback(e)
        self.stop()

    @property
    def name(self):
        return convert_camelcase(self.case_func.__name__)

    @property
    def pretty_name(self):
        return self.case_func.__name__.replace('_', ' ')

    @property
    def doc(self):
        return self.case_func.__doc__

    @property
    def success(self):
        return (not self.failed and not self.error and
                len([exp for exp in self.expects if not exp.success]) == 0)


class Describe(EventDispatcher):
    __FIXTURE__ = False

    def __init__(self, parent=None):
        super(Describe, self).__init__()
        self.parent = parent
        self.cases = self.__wrappers__
        self.describes = [desc_type(parent=self)
                          for desc_type in self.describe_types]

    @property
    def name(self):
        return convert_camelcase(self.__class__.__name__)

    @property
    def doc(self):
        return type(self).__doc__

    @property
    def success(self):
        ok = True
        case_successes = [case.success for case in self.cases]
        spec_successes = [spec.success for spec in self.describes]
        if case_successes and False in case_successes:
            ok = False

        if spec_successes and False in spec_successes:
            ok = False
        return ok

    @property
    def __wrappers__(self):
        wrappers = []
        for case_func in self.case_funcs:
            case_func, metadata = extract_metadata(case_func)
            wrappers.append(CaseWrapper(case_func, parent=self,
                                        metadata=metadata))
        return wrappers

    @classmethod
    def __cls_members__(cls):
        all_members = {}
        classes = list(cls.__bases__) + [cls]

        for klass in classes:
            pairs = dict((key, val) for key, val in vars(klass).items())
            all_members.update(pairs)

        return all_members

    @classmethod
    def __get_all_child_describes__(cls):
        members = cls.__cls_members__()
        child_describes = [val for key, val in members.items()
                           if Describe.plugin_filter(val)]
        all_children = child_describes + [cls]

        for child in child_describes:
            all_children.extend(child.__get_all_child_describes__())
        return set(all_children)

    @property
    def __members__(self):
        return type(self).__cls_members__()

    @property
    def describe_types(self):
        return [val for key, val in self.__members__.items()
                if Describe.plugin_filter(val)]

    @property
    def case_funcs(self):
        return [val for key, val in self.__members__.items()
                if Describe.case_filter(val)]

    @property
    def top_parent(self):
        parent_above = last_parent = self.parent or self

        while parent_above is not None:
            last_parent = parent_above
            parent_above = parent_above.parent

        return last_parent

    @classmethod
    def is_fixture(cls):
        return vars(cls).get('__FIXTURE__') is True

    def before_all(self):
        pass

    def after_all(self):
        pass

    def before_each(self):
        pass

    def after_each(self):
        pass

    def execute(self, select_metadata=None):

        if select_metadata:
            self.cases = find_by_metadata(select_metadata, self.cases)
            self.describes = children_with_tests_with_metadata(
                select_metadata, self)

        # If it doesn't have tests or describes don't run it
        if len(self.cases) <= 0 and len(self.describes) <= 0:
            return

        self.top_parent.dispatch(DescribeEvent(DescribeEvent.START, self))

        self.before_all()

        # Execute Cases
        for case in self.cases:
            self.before_each()
            case.execute(context=self)
            self.after_each()

            self.top_parent.dispatch(TestEvent(case))

        # Execute Suites
        for describe in self.describes:
            describe.execute(select_metadata=select_metadata)

        self.after_all()
        self.top_parent.dispatch(DescribeEvent(DescribeEvent.COMPLETE, self))

    @classmethod
    def plugin_filter(cls, other):
        if not isinstance(other, type):
            return False

        if hasattr(other, 'is_fixture') and other.is_fixture():
            return False

        return (issubclass(other, Describe) and
                other is not cls
                and other is not Spec
                and other is not DataDescribe)

    @classmethod
    def case_filter(cls, obj):
        if type(obj) is not FunctionType:
            return False

        func_name = obj.__name__
        return (not func_name.startswith('_') and
                not func_name == 'execute' and
                not func_name == 'before_each' and
                not func_name == 'after_each' and
                not func_name == 'before_all' and
                not func_name == 'after_all')


class Spec(Describe):
    pass


class DataDescribe(Describe):
    DATASET = {}

    def __init__(self, parent=None):
        super(DataDescribe, self).__init__(parent=parent)
        self.cases = []

        # Generate new functions and monkey-patch
        for case_func in self.case_funcs:
            extracted_func, base_metadata = extract_metadata(case_func)

            for name, data in self.DATASET.items():
                args, meta = data, dict(base_metadata)

                # Handle complex dataset item
                if 'args' in data and 'meta' in data:
                    args = data.get('args', {})
                    meta.update(data.get('meta', {}))

                # Extract name, args and duplicate function
                func_name = '{0}_{1}'.format(extracted_func.__name__, name)
                new_func = copy_function(extracted_func, func_name)
                kwargs = get_function_kwargs(extracted_func, args)

                # Monkey-patch and add to cases list
                setattr(self, func_name, new_func)
                self.cases.append(CaseWrapper(new_func, parent=self,
                                              execute_kwargs=kwargs,
                                              metadata=meta))


def fixture(cls):
    """ A simple decorator to set the fixture flag on the class."""
    setattr(cls, '__FIXTURE__', True)
    return cls


def copy_function(func, name):
    py3 = (3, 0, 0)
    code = (func.func_code
            if sys.version_info < py3 else func.__code__)
    globals = (func.func_globals
               if sys.version_info < py3 else func.__globals__)

    return FunctionType(code, globals, name)

def get_function_kwargs(old_func, new_args):
    args, _, _, defaults = inspect.getargspec(old_func)
    if 'self' in args:
        args.remove('self')

    # Make sure we take into account required arguments
    izip = (itertools.izip_longest
            if sys.version_info < (3, 0, 0) else itertools.zip_longest)
    kwargs = dict(
        izip(args[::-1], list(defaults or ())[::-1], fillvalue=None))

    kwargs.update(new_args)
    return kwargs

class DescribeEvent(Event):
    START = 'start'
    COMPLETE = 'complete'


class TestEvent(Event):
    COMPLETE = 'test_complete'

    def __init__(self, payload):
        super(TestEvent, self).__init__(TestEvent.COMPLETE, payload=payload)


class FailedRequireException(Exception):
    pass


class TestSkippedException(Exception):
    def __init__(self, func, reason=None):
        self.func = func
        self.reason = reason


class TestIncompleteException(Exception):
    def __init__(self, func, reason=None):
        self.func = func
        self.reason = reason
