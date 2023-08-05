from nose.plugins import Plugin
from unittest import TestCase
from pspecs import Context

class SpecsPlugin(Plugin):

    def wantFile(self, file):
        return file.endswith('_spec.py')

    def wantModule(self, module):
        return True

    def makeTest(self, context, parent):
        if issubclass(context, Context):
            tests = context.discovered_test_cases()
            for test in tests:
                yield test

    def wantMethod(self, method):
        return False

    def wantFunction(self, function):
        return False

    def wantClass(self, cls):
        if issubclass(cls, Context):
            return True
