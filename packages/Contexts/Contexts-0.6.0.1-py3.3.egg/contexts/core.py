import inspect
import itertools
import os
import random
import types
from contextlib import contextmanager
from . import discovery
from . import errors
from . import finders


class Suite(object):
    def __init__(self, source, shuffle):
        self.source = source
        self.shuffle = shuffle

    def run(self, reporter_notifier):
        with reporter_notifier.run_suite(self):
            for cls in self.get_classes(reporter_notifier):
                self.run_class(cls, reporter_notifier)

    def get_classes(self, reporter_notifier):
        if isinstance(self.source, types.ModuleType):
            list_of_lists = [list(finders.find_specs_in_module(self.source))]
        elif isinstance(self.source, str) and os.path.isfile(self.source):
            module = discovery.import_from_file(self.source)
            list_of_lists = [list(finders.find_specs_in_module(module))]
        elif isinstance(self.source, str) and os.path.isdir(self.source):
            module_specs = discovery.find_modules(self.source)
            list_of_lists = []
            for module_spec in module_specs:
                with reporter_notifier.importing(module_spec):
                    module = discovery.load_module(*module_spec)
                    module_classes = list(finders.find_specs_in_module(module))
                    list_of_lists.append(module_classes)
        else:
            list_of_lists = [[self.source]]

        ret = []
        for l in list_of_lists:
            if self.shuffle:
                random.shuffle(l)
            ret.extend(l)

        return ret

    def run_class(self, cls, reporter_notifier):
        with reporter_notifier.run_class(cls):
            for example in get_examples(cls):
                context = Context(cls(), example, self.shuffle)
                context.run(reporter_notifier)

def get_examples(cls):
    examples_method = finders.find_examples_method(cls)
    examples = examples_method()
    return examples if examples is not None else [_NullExample()]


class _NullExample(object):
    null_example = True


class Context(object):
    def __init__(self, instance, example, shuffle):
        finder = finders.MethodFinder(instance)
        setups, actions, assertions, teardowns = finder.find_special_methods()
        assert_no_ambiguous_methods(setups, actions, assertions, teardowns)
        self.instance = instance
        self.setups = setups
        self.actions = actions
        self.assertions = [Assertion(f) for f in assertions]
        self.teardowns = teardowns
        self.example = example
        self.name = instance.__class__.__name__

        if shuffle:
            random.shuffle(self.assertions)

    def run_setup(self):
        for setup in self.setups:
            run_with_test_data(setup, self.example)

    def run_action(self):
        for action in self.actions:
            run_with_test_data(action, self.example)

    def run_assertions(self, reporter_notifier):
        for assertion in self.assertions:
            assertion.run(self.example, reporter_notifier)

    def run_teardown(self):
        for teardown in self.teardowns:
            run_with_test_data(teardown, self.example)

    def run(self, reporter_notifier):
        if not self.assertions:
            return
        with reporter_notifier.run_context(self):
            try:
                self.run_setup()
                self.run_action()
                self.run_assertions(reporter_notifier)
            finally:
                self.run_teardown()

def assert_no_ambiguous_methods(*iterables):
    for a, b in itertools.combinations((set(i) for i in iterables), 2):
        overlap = a & b
        if overlap:
            msg = "The following methods are ambiguously named:\n"
            msg += '\n'.join([func.__qualname__ for func in overlap])
            raise errors.MethodNamingError(msg)


class Assertion(object):
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def run(self, test_data, reporter_notifier):
        with reporter_notifier.run_assertion(self):
            run_with_test_data(self.func, test_data)


def run_with_test_data(func, test_data):
    sig = inspect.signature(func)
    if not isinstance(test_data, _NullExample) and sig.parameters:
        func(test_data)
    else:
        func()


class ReporterNotifier(object):
    def __init__(self, *reporters):
        self.reporters = []
        for reporter in reporters:
            self.reporters.append(reporter)

    @property
    def failed(self):
        return any(r.failed for r in self.reporters if hasattr(r, 'failed'))

    def call_reporters(self, method, *args):
        for reporter in self.reporters:
            getattr(reporter, method)(*args)

    @contextmanager
    def run_suite(self, suite):
        self.call_reporters("suite_started", suite)
        try:
            yield
        except Exception as e:
            self.call_reporters("unexpected_error", e)
        self.call_reporters("suite_ended", suite)

    @contextmanager
    def run_context(self, context):
        self.call_reporters("context_started", context)
        try:
            yield
        except Exception as e:
            self.call_reporters("context_errored", context, e)
        else:
            self.call_reporters("context_ended", context)

    @contextmanager
    def run_assertion(self, assertion):
        self.call_reporters("assertion_started", assertion)
        try:
            yield
        except AssertionError as e:
            self.call_reporters("assertion_failed", assertion, e)
        except Exception as e:
            self.call_reporters("assertion_errored", assertion, e)
        else:
            self.call_reporters("assertion_passed", assertion)

    @contextmanager
    def run_class(self, cls):
        try:
            yield
        except Exception as e:
            self.call_reporters("unexpected_error", e)

    @contextmanager
    def importing(self, module_spec):
        try:
            yield
        except Exception as e:
            self.call_reporters("unexpected_error", e)
