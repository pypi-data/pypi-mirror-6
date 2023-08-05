from formskit.validators import ValidationError


class Field(object):

    def __init__(self, name, validators=None, label=None, ignore=False):
        self.name = name
        self.label = label
        self.validators = validators or []
        self.ignore = ignore
        self.value = None
        self.form = None
        self.message = None
        self.error = False

    def initForm(self, form):
        self.form = form

    def validate(self):
        try:
            for validator in self.validators:
                validator.setField(self)
                validator(self.value)
            self.message = None
            self.error = False
            return True
        except ValidationError as ex:
            self.message = ex.message
            self.error = True
            return False

class Button(Field):
    def __init__(self, name, label):
        super(Button, self).__init__(name, label=label, ignore=True)
