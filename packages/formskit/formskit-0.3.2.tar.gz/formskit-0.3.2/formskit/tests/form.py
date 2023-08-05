from mock import MagicMock

from formskit import Form, Field, Button
from formskit.errors import BadValue
from formskit.tests.base import FormskitTestCase
from formskit.validators import NotEmpty


class SampleObject(object):

    def __init__(self, name1='value1', name2='value2'):
        self.name1 = name1
        self.name2 = name2


class SampleObject2(object):

    def __init__(self, name1='value1'):
        self.name1 = name1


class Form1(Form):

    submitTest = False
    overal = False
    name1 = 'name1'

    def submit(self, data):
        self._test_data = data
        self.submitTest = True

    def overalValidation(self, data):
        return self.overal

    def createForm(self):
        self.addField(Field(self.name1))


class Form2(Form):
    name1 = 'name1'
    name2 = 'name2'

    def createForm(self):
        self.addField(Field(self.name1, [NotEmpty()]))
        self.addField(Field(self.name2, [NotEmpty()]))
        self.addField(Button('button', label=u'Zaloguj'))


class Form3(Form):
    name1 = 'name1'
    name2 = 'name2'

    def createForm(self):
        self.addField(Field(self.name1, label=u'my label'))
        self.addField(Field(self.name2, [NotEmpty()]))
        self.addField(Button('button', label=u'Zaloguj'))


class FormTest(FormskitTestCase):

    def test_get_label(self):
        form = Form3()
        self.assertEqual('my label', form.get_label('name1'))

    def test_get_error(self):
        form = Form3()
        form.fields['something'] = [MagicMock()]
        form.fields['something'][0].error = 'error'
        self.assertEqual('error', form.get_error('something'))

    def test_get_error_fail(self):
        form = Form3()
        self.assertEqual(False, form.get_error('something'))

    def test_get_message(self):
        form = Form3()
        form.fields['something'] = [MagicMock()]
        form.fields['something'][0].message = 'message'
        self.assertEqual('message', form.get_message('something'))

    def test_get_message_fail(self):
        form = Form3()
        self.assertEqual(None, form.get_message('something'))

    def test_get_value(self):
        form = Form3()
        form.fields['something'] = [MagicMock()]
        form.fields['something'][0].value = 'value'
        self.assertEqual('value', form.get_value('something'))

    def test_get_value_fail(self):
        form = Form3()
        self.assertEqual(None, form.get_value('something'))

    def test_name(self):
        self.assertEqual(Form1().name, 'Form1')

    def test_addField(self):
        name = 'rosomak'
        field = Field(name)
        form = Form1()
        form.addField(field)

        self.assertTrue(name in form.field_patterns)
        self.assertEqual(field, form.field_patterns[name])
        self.assertEqual(form, field.form)

    def test_gatherDataFromFields(self):
        name1 = 'rosomak'
        value1 = 'wolverine'
        name2 = 'stefan'
        value2 = 'robin'

        field1 = Field(name1)
        field2 = Field(name2)

        form = Form1()
        form.addField(field1)
        form.addField(field2)
        form._assign_field_value(name1, value1)
        form._assign_field_value(name2, value2)

        data = form.gatherDataFromFields()
        self.assertTrue(name1 in data)
        self.assertTrue(name2 in data)
        self.assertEqual([value1, ], data[name1])
        self.assertEqual([value2, ], data[name2])

    def test_createForm(self):
        form = Form2()

        self.assertTrue(form.name1 in form.field_patterns)
        self.assertTrue(form.name2 in form.field_patterns)

    def test_isThisFormSubmited(self):
        form = Form2()

        self.assertFalse(form._isThisFormSubmited({}))
        self.assertFalse(
            form._isThisFormSubmited({'form_name': ['Formasd2', ]}))
        self.assertTrue(form._isThisFormSubmited({'form_name': ['Form2', ]}))

    def test_gatherFormsData(self):
        form = Form1()

        name1 = 'name1'
        name2 = 'name2'

        field1 = Field(name1)
        field2 = Field(name2)
        form.addField(field1)
        form.addField(field2)

        value1 = ['value1', ]
        value2 = ['value2', ]

        data = {
            'form_name': 'Form1',
            name1: value1,
        }

        data[name2] = value2

        form._gatherFormsData(data)

        self.assertEqual(value1[0], form.fields[name1][0].value)
        self.assertEqual(value2[0], form.fields[name2][0].value)

        data['name3'] = 'value3'
        self.assertRaises(BadValue, form._gatherFormsData, data)

    def test_validateFields(self):
        form = Form3()
        form._assign_field_value(form.name1, '')
        form._assign_field_value(form.name2, '')

        self.assertFalse(form._validateFields())
        self.assertFalse(form.fields['name1'][0].error)
        self.assertTrue(form.fields['name2'][0].error)
        self.assertNone(form.fields['name1'][0].message)
        self.assertEqual(NotEmpty.message, form.fields['name2'][0].message)

        form.fields[form.name1][0].value = 'asasdsd'
        self.assertFalse(form._validateFields())
        self.assertFalse(form.fields['name1'][0].error)
        self.assertTrue(form.fields['name2'][0].error)
        self.assertNone(form.fields['name1'][0].message)
        self.assertEqual(NotEmpty.message, form.fields['name2'][0].message)

        form.fields[form.name2][0].value = 'asd'
        self.assertTrue(form._validateFields())
        self.assertFalse(form.fields['name1'][0].error)
        self.assertFalse(form.fields['name2'][0].error)
        self.assertNone(form.fields['name1'][0].message)
        self.assertNone(form.fields['name2'][0].message)

    def test_validate_and_submit(self):
        form = Form1()
        form.overal = False

        self.assertFalse(form._validate_and_submit())
        self.assertFalse(form.submitTest)

        form = Form1()
        form.overal = True
        self.assertTrue(form._validate_and_submit())
        self.assertTrue(form.submitTest)
        self.assertEqual({}, form._test_data)

    def test_call(self):
        form = Form1()

        value1 = ['value1', ]

        data = {
            form.form_name_value: ['bad name', ],
            form.name1: value1,
        }

        self.assertNone(form(data))

        data[form.form_name_value] = [form.name, ]
        self.assertFalse(form(data))
        self.assertFalse(form.submitTest)

        form.overal = True
        self.assertTrue(form(data))
        self.assertTrue(form.submitTest)
        self.assertEqual({form.name1: value1}, form._test_data)

    def test_ignore(self):
        good_name = 'name1'
        good_value = ['value1', ]
        button_name = 'button1'
        form = Form1()
        form.overal = True
        form.addField(Button(button_name, 'label'))
        form.addField(Field(good_name))

        data = {
            form.form_name_value: [form.name, ],
            good_name: good_value,
        }

        self.assertTrue(form(data))
        self.assertEqual(good_value[0], form.fields[good_name][0].value)
        self.assertEqual(good_value, form._test_data[good_name])
        self.assertFalse(button_name in form._test_data)

    def test_assign_field_value(self):
        form = Form1()
        form.fields = {}
        form._assign_field_value('name1', 'value1')

        self.assertEqual(Field, type(form.fields['name1'][0]))
        self.assertEqual(1, len(form.fields['name1']))

    def test_missing_value(self):
        form = Form2()
        result = form({
            'form_name': ['Form2',],
            'name1': ['one'],
        })
        self.assertTrue(result is False)

    def test_missing_value_2(self):
        form = Form2()
        result = form({
            'form_name': ['Form2',],
            'name1': ['one'],
            'name2': [],
        })
        self.assertTrue(result is False)

    def test_missing_value_3(self):
        form = Form2()
        result = form({
            'form_name': ['Form2',],
            'name1': ['one'],
            'name2': [''],
        })
        self.assertTrue(result is False)

    def test_not_missing_value(self):
        form = Form2()
        result = form({
            'form_name': ['Form2',],
            'name1': ['one'],
            'name2': ['two'],
        })
        self.assertTrue(result is True)


class FormUpdateTest(FormskitTestCase):

    def setUp(self):
        super(FormUpdateTest, self).setUp()
        self.form = Form3()

    def test_simple(self):
        s1 = SampleObject()
        self.form.update(s1)

        self.assertEqual(s1.name1, self.form.fields['name1'][0].value)
        self.assertEqual(s1.name2, self.form.fields['name2'][0].value)

    def test_with_names(self):
        s3 = SampleObject('value1_3', 'value2_3')
        self.form.update(s3, ['name1'])

        self.assertEqual(s3.name1, self.form.fields['name1'][0].value)
        self.assertTrue('name2' not in self.form.fields)

    def test_dict(self):
        s4 = {
            'name1': 'value1_4',
            'name2': 'value2_4',
        }

        self.form.update(s4, method='dict')

        self.assertEqual(s4['name1'], self.form.fields['name1'][0].value)
        self.assertEqual(s4['name2'], self.form.fields['name2'][0].value)

    def test_missing_attribute(self):
        s5 = SampleObject2('value1_5')
        self.assertRaises(AttributeError, self.form.update, s5)

    def test_obj_default_none(self):
        s6 = SampleObject2('value1_6')
        self.form.update(s6, method='obj_default_none')
        self.assertEqual(s6.name1, self.form.fields['name1'][0].value)
        self.assertEqual(None, self.form.fields['name2'][0].value)

    def test_own_get_method(self):
        s7 = SampleObject2('value1_7')

        def method(obj, name):
            return name
        self.form.update(s7, method=method)
        self.assertEqual('name1', self.form.fields['name1'][0].value)
        self.assertEqual('name2', self.form.fields['name2'][0].value)

    def test_ignore_missing(self):
        s8 = SampleObject2('value1_8')
        self.form.update(s8, ignore_missing=True)
        self.assertEqual(s8.name1, self.form.fields['name1'][0].value)
        self.assertTrue('name2' not in self.form.fields)

    def test_update_after_change(self):
        changed_value = 'value3_9'
        s9 = SampleObject('value1_9', 'value2_9')
        self.form._assign_field_value('name1', changed_value)
        self.form.update(s9)

        self.assertEqual(s9.name1, self.form.fields['name1'][0].value)
        self.assertEqual(s9.name2, self.form.fields['name2'][0].value)
