from unittest import TestCase
alltests = []


class FormskitTestCaseType(type):

    def __init__(cls, name, bases, dct):
        super(FormskitTestCaseType, cls).__init__(name, bases, dct)
        if not name in ['FormskitTestCase', 'ValidatorTest']:
            alltests.append(cls)


class FormskitTestCase(TestCase, metaclass=FormskitTestCaseType):

    def assertNone(self, obj):
        return self.assertEqual(None, obj)
