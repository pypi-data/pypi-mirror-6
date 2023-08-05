from unittest import TestCase
alltests = []
from six import add_metaclass


class FormskitTestCaseType(type):

    def __init__(cls, name, bases, dct):
        super(FormskitTestCaseType, cls).__init__(name, bases, dct)
        if not name in ['FormskitTestCase', 'ValidatorTest']:
            alltests.append(cls)


@add_metaclass(FormskitTestCaseType)
class FormskitTestCase(TestCase):

    def assertNone(self, obj):
        return self.assertEqual(None, obj)
