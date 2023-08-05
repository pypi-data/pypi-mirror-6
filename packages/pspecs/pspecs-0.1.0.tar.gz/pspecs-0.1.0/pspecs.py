import inspect
from unittest import TestCase

__version__ = '0.1.0'


class EmptyContext(object):
    _parent_context = None

    NO_ATTRIBUTE = '__no_attr'

    @classmethod
    def tests(cls):
        return []

    @classmethod
    def factory_methods(cls):
        return {}

    @classmethod
    def hooks(cls, type):
        return []

    def __getattr__(self, item):
        return self.NO_ATTRIBUTE

class SpecTestCase(TestCase):

    def __init__(self, context, method):
        super(SpecTestCase, self).__init__()
        self.context = context
        self.method = method

    def runTest(self):
        for before in self.context.hooks('before'):
            before(self.context)
        self.method(self.context)
        for after in reversed(self.context.hooks('after')):
            after(self.context)

    def name(self):
        return self.context.name() + ' -> ' + self.method.__name__

    def id(self):
        return self.name()

    def __repr__(self):
        return self.name()

class let(object):
    """A @property that is only evaluated once."""

    def __init__(self, deferred):
        self._deferred = deferred
        self.__doc__ = deferred.__doc__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = self._deferred(obj)
        setattr(obj, self._deferred.__name__, value)
        return value

class MetaContext(type):

    def __new__(mcs, cls, base, dict):
        class_type = type.__new__(mcs, cls, base, dict)

        if cls == 'Context':
            return class_type

        for name, value in dict.items():
            if name.find('let_') == 0:
                dict[name[4:]] = let(value)

        return class_type


class Context(object):

    __metaclass__ = MetaContext

    _uses = []
    _parent_context = EmptyContext

    def use(self, context):
        self._uses.append(context())

    @classmethod
    def set_parent(cls, parent):
        cls._parent_context = parent

        return cls

    def name(self):
        if isinstance(self.parent, EmptyContext):
            return self.__class__.__name__
        return self.parent.name() + ' -> ' + self.__class__.__name__

    @classmethod
    def discovered_test_cases(cls, parent_context=EmptyContext()):
        discovered = []
        for name, method in cls.__dict__.items():
            if isinstance(method, let):
                continue
                
            if name.find('it') == 0 or name.find('test') == 0:
                ctx = cls()
                ctx.parent = parent_context
                discovered.append(SpecTestCase(ctx, method))

        for child in cls.children_contexts():
            parent = cls()
            parent.parent = parent_context
            for child_test in child.discovered_test_cases(parent):
                discovered.append(child_test)

        return discovered

    @classmethod
    def factory_methods(cls):
        let = cls._parent_context.factory_methods()
        for name, method in cls.__dict__.items():
            if name.find('let_') == 0:
                let[name[4:]] = method

        return let

    @classmethod
    def hooks(cls, type):
        hooks = cls._parent_context.hooks(type)
        if type in cls.__dict__:
            hooks.append(cls.__dict__[type])

        return hooks

    @classmethod
    def children_contexts(cls):
        sub_contexts = []
        for name, children_context in cls.__dict__.items():
            if inspect.isclass(children_context) \
                and name != '_parent_context' \
                and issubclass(children_context, Context):
                    sub_contexts.append(children_context.set_parent(cls))

        return sub_contexts

    def __getattr__(self, attr):
        """ This method will be called for an attribute lookup, when one is not found in the object __dict__
        The lookup chain is:
         1. search for a let_attr factory method and build the attribute from that
         2. go to every self.use(Context) context in the reverse order they where declared
         3. go to the parent context
        """
        if attr in self.factory_methods():
            return self._build_attr(attr)

        for context in self._uses:
            value = getattr(context, attr)
            if value != EmptyContext.NO_ATTRIBUTE:
                return value

        value = getattr(self.parent, attr)
        if value == EmptyContext.NO_ATTRIBUTE:
            raise AttributeError('Attribute %s not found' % attr)

        return value

    def _build_attr(self, attr):
        """ Build the attribute passing the current context as an instance
        Also, set the build value in the class __dict__, so that it will not be build again
        """

        value = self.factory_methods()[attr](self)
        setattr(self, attr, value)

        return getattr(self, attr)
