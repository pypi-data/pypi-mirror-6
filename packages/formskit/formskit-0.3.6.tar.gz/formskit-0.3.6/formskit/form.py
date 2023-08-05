from copy import copy

from formskit.errors import BadValue
from formskit.formvalidators import FormValidationError


class Form(object):

    form_name_value = 'form_name'

    def __init__(self):
        self.fields = {}
        self.field_patterns = {}
        self.formValidators = []
        self.createForm()
        self.error = False
        self.message = None

    @property
    def name(self):
        return self.__class__.__name__

    def addField(self, field):
        self.field_patterns[field.name] = field
        field.initForm(self)

    def addFormValidator(self, validator):
        validator.setForm(self)
        self.formValidators.append(validator)

    def gatherDataFromFields(self):
        data = {}
        for name, fields in self.fields.items():
            data[name] = []
            if not fields[0].ignore:
                for field in fields:
                    data[name].append(field.value)
        return data

    def _isThisFormSubmited(self, data):
        return self.form_name_value in data and data[self.form_name_value] == [self.name, ]

    def _assign_field_value(self, name, value):
        if not name in self.fields:
            self.fields[name] = []
        field = copy(self.field_patterns[name])
        self.fields[name].append(field)
        field.value = value

    def _assign_missing_values(self):
        field_names = []
        for name, value in self.field_patterns.items():
            if not value.ignore:
                field_names.append(name)

        for name in field_names:
            if name not in self.fields:
                self._assign_field_value(name, None)


    def _gatherFormsData(self, data):
        self.fields = {}
        data = dict(data)
        data.pop(self.form_name_value)

        field_names = list(self.field_patterns)

        for name, value in data.items():
            if name in field_names:
                for small_value in value:
                    self._assign_field_value(name, small_value)
            else:
                raise BadValue(name)

        self._assign_missing_values()

    def _validateFields(self):
        def validateFields():
            validation = True
            for name, fields in self.fields.items():
                if not fields[0].ignore:
                    for field in fields:
                        validation &= field.validate()
            return validation

        def validateGlobalValidators():
            try:
                for formValidator in self.formValidators:
                    formValidator()
            except FormValidationError as er:
                self.message = er.message
                self.error = True
                return False
            return True
        #----------------------------------------------------------------------
        validation = validateFields()
        if validation:
            validation = validateGlobalValidators()
        return validation

    def _validate_and_submit(self):
        data = self.gatherDataFromFields()
        if self._validateFields():
            if self.overalValidation(data):
                self.submit(data)
                return True
            else:
                self.error = True
        return False

    def __call__(self, data):
        if self._isThisFormSubmited(data):
            self._gatherFormsData(data)
            return self._validate_and_submit()

    def update(self, obj, names=None, method='obj', ignore_missing=False):
        def getattr_obj(obj, name):
            return getattr(obj, name)

        def getattr_dict(obj, name):
            return obj[name]

        def getattr_obj_default_none(obj, name):
            return getattr(obj, name, None)

        def get_method(method):
            getattr_funs = {
                'obj': getattr_obj,
                'dict': getattr_dict,
                'obj_default_none': getattr_obj_default_none,
            }
            if type(method) == str:
                return getattr_funs[method]
            else:
                return method

        def make_names(names):
            if names is None:
                return list(self.field_patterns)
            else:
                return names

        def set_form_field(name, obj, get):
            if not self.field_patterns[name].ignore and self.field_patterns[name].value in [None, '']:
                data = get(obj, name)
                if name in self.fields:
                    self.fields[name][0].value = data
                else:
                    self._assign_field_value(name, data)

        get = get_method(method)
        names = make_names(names)
        if ignore_missing:
            for name in names:
                try:
                    set_form_field(name, obj, get)
                except (AttributeError, KeyError):
                    continue
        else:
            for name in names:
                set_form_field(name, obj, get)

    def overalValidation(self, data):
        return True  # pragma: no cover

    def createForm(self):
        pass  # pragma: no cover

    def submit(self, data):
        pass  # pragma: no cover

    def get_label(self, name):
        return self.field_patterns[name].label

    def get_error(self, name, index=0):
        if name in self.fields:
            fields = self.fields[name]
            if len(fields) > index:
                return fields[index].error
        return False

    def get_message(self, name, index=0):
        if name in self.fields:
            fields = self.fields[name]
            if len(fields) > index:
                return fields[index].message
        return None

    def get_value(self, name, index=0):
        if name in self.fields:
            fields = self.fields[name]
            if len(fields) > index:
                return fields[index].value
        return None
