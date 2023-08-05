# encoding: utf8
import re
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):

    def __init__(self, validator):
        self.validator = validator.__class__.__name__
        self.message = validator.message


class Validator(object):

    def __init__(self, message=None):
        if message:
            self.message = message

    def setField(self, field):
        self.field = field

    def __call__(self, value):
        if not self.validate(value):
            raise ValidationError(self)


class NotEmpty(Validator):
    message = u"This element is mandatory."

    def validate(self, value):
        if value == None:
            return False
        elif type(value) == str and value.strip() == '':
            return False
        elif type(value) == bytes and value.strip() == b'':
            return False
        elif type(value) in [list, dict, tuple] and len(value) == 0:
            return False
        return True


class IsDigit(Validator):
    message = u'This element must be a digit.'

    def validate(self, value):
        if re.search('^-{0,1}[0-9]+$', value):
            return True
        else:
            return False


class IsDecimal(Validator):
    message = u'This element must be a decimal.'

    def validate(self, value):
        try:
            Decimal(value)
            return True
        except InvalidOperation:
            return False


class Email(Validator):
    message = u"Email is not valid."

    def validate(self, value):
        if len(value) > 7:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", value) != None:
                return True
        return False
