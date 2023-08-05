from formskit.tests.base import FormskitTestCase
from formskit import Field, Button
from formskit.validators import NotEmpty, IsDigit


class FieldTest(FormskitTestCase):

    def test_creation(self):
        name = 'name'
        label = 'label'
        validators = [None, 1]
        field = Field(name, validators, label)

        self.assertEqual(name, field.name)
        self.assertEqual(label, field.label)
        self.assertEqual(validators, field.validators)
        self.assertEqual(None, field.value)
        self.assertEqual(None, field.form)
        self.assertEqual(None, field.message)
        self.assertFalse(field.ignore)

        field = Field(name, validators, label, True)

        self.assertEqual(name, field.name)
        self.assertEqual(label, field.label)
        self.assertEqual(validators, field.validators)
        self.assertEqual(None, field.value)
        self.assertEqual(None, field.form)
        self.assertEqual(None, field.message)
        self.assertTrue(field.ignore)


    def test_init(self):
        form = 123
        field = Field(None, None, None)
        field.initForm(form)

        self.assertEqual(form, field.form)

    def test_validate(self):
        empty = NotEmpty()
        field = Field('name', [empty,])

        self.assertEqual(False, field.validate())
        self.assertEqual(field, empty.field)

        field.value = 'green'

        self.assertEqual(True, field.validate())
        self.assertEqual(field, empty.field)

    def test_two_validators(self):
        field = Field('name', [NotEmpty(), IsDigit()])

        self.assertEqual(False, field.validate())

        field.value = 'green'

        self.assertEqual(False, field.validate())

        field.value = '15'

        self.assertEqual(True, field.validate())

    def test_buttons(self):
        label = 'button test'
        name = 'button name'
        field = Button(name, label)
        self.assertTrue(field.ignore)
        self.assertEqual(name, field.name)
        self.assertEqual(label, field.label)
