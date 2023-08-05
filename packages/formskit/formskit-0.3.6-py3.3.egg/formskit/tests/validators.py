from formskit.tests.base import FormskitTestCase
from formskit.field import Field
import formskit.validators as VAL


class ValidatorTest(FormskitTestCase):
    cls = None
    good_samples = None
    bad_samples = None

    def test_create(self):
        sample_text = 'something'
        validator = self.cls(sample_text)

        self.assertEqual(sample_text, validator.message)

    def test_success(self):
        validator = self.cls('')

        for sample in self.good_samples:
            self.assertNone(validator(sample))

    def test_fail(self):
        validator = self.cls('')

        for sample in self.bad_samples:
            self.assertRaises(VAL.ValidationError, validator, sample)

    def test_setForm(self):
        field = Field('my field')
        validator = self.cls('')
        validator.setField(field)

        self.assertEqual(field, validator.field)


class NotEmptyValidatorTest(ValidatorTest):
    cls = VAL.NotEmpty

    good_samples = [
        'z', '0', '12312312dasd213123', ',', ' ad sda ',
    ]

    bad_samples = [
        ' ', '', None, [], {}, b'',
    ]


class IsDigitValidatorTest(ValidatorTest):
    cls = VAL.IsDigit

    good_samples = [
        '1', '123123123', '012312', '-123123',
    ]

    bad_samples = [
        'a', '', '-123213.12323', '2a',
    ]

class EmailValidatorTest(ValidatorTest):
    cls = VAL.Email

    good_samples = [
        'msocek@gmail.com',
        '1asd@asdasd.sadad.pl',
    ]

    bad_samples = [
        'a', '', '-123213.12323', '2a',
        ' ', '@asdweq.asdad.pl', '1asd@asdasd.sadad.asdpl',
    ]

class IsDecimalTest(ValidatorTest):
    cls = VAL.IsDecimal

    good_samples = [
        '1',
        '1.2',
        '1.2213123123123123',
        '123123123.123123'
        '234234234234',
        '-123123.123123',
    ]

    bad_samples = [
        'a', '', '-123213,12323', '2a',
        ' ', '@asdweq.asdad.pl', '1asd@asdasd.sadad.asdpl',
    ]
