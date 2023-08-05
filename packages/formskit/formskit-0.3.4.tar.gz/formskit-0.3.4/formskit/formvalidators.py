# encoding: utf8
class FormValidationError(Exception):

    def __init__(self, validator):
        self.validator = validator.__class__.__name__
        self.message = validator.message


class FormValidator(object):

    message = None

    def setForm(self, form):
        self.form = form

    def __call__(self):
        if not self.validate():
            raise FormValidationError(self)


class MustBeTheSame(FormValidator):

    message_tpl = '%s must be the same!'

    def __init__(self, names, label):
        self.names = names
        self.label = label

    @property
    def message(self):
        return self.message_tpl % (self.label,)

    def validate(self):
        values = []
        for name in self.names:
            for field in self.form.fields[name]:
                values.append(field.value)
        first = values.pop(0)
        for value in values:
            if first != value:
                return False
        return True
