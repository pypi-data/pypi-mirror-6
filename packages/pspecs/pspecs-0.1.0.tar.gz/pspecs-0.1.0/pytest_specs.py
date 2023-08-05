import pytest
from pspecs import Context
import inspect

def pytest_addoption(parser):
    group = parser.getgroup('specs group')
    group.addoption('--specs', action='store_true', help='Collects specs')

def pytest_collect_file(path, parent):
    if parent.config.option.specs and path.ext == '.py' and path.strpath.find('_spec.py') != -1:
        return SpecFile(path, parent)

class SpecFile(pytest.File):
    def collect(self):

        module = self.fspath.pyimport()
        for _, context in inspect.getmembers(module, inspect.isclass):
            if issubclass(context, Context):
                for test in context.discovered_test_cases():
                    yield SpecItem(context.__class__.__name__, self, test)

class SpecItem(pytest.Item):

    def __init__(self, name, parent, test):
        super(SpecItem, self).__init__(name, parent)
        self.test = test

    def runtest(self):
        self.test.run()

    def reportinfo(self):
        return self.fspath, 0, self.test.name()