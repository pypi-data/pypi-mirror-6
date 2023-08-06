from django.utils import unittest
from django.db.models import Model, CharField
from django.forms import Form, ModelForm

from vies import fields, VATIN
from vies import models

VALID_VIES = 'DE284754038'
VALID_VIES_COUNTRY_CODE = 'DE'
VALID_VIES_NUMBER = '284754038'


class VIESModel(Model):
    vat = models.VATINField()


class EmptyVIESModel(Model):
    name = CharField(default='John Doe', max_length='50')
    vat = models.VATINField(blank=True, null=True)


class VIESModelForm(ModelForm):
    class Meta:
        model = VIESModel


class EmptyVIESModelForm(ModelForm):
    class Meta:
        model = EmptyVIESModel


class VIESForm(Form):
    vat = fields.VATINField()


class EmptyVIESForm(Form):
    vat = fields.VATINField(required=False)


class VIESTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_creation(self):
        try:
            VATIN(VALID_VIES_COUNTRY_CODE, VALID_VIES_NUMBER)
        except Exception, e:
            self.fail(e.message)

    def test_verified(self):
        with self.assertRaises(ValueError):
            VATIN('xx', VALID_VIES_NUMBER)

    def test_country_code_getter(self):
        v = VATIN(VALID_VIES_COUNTRY_CODE.lower(), VALID_VIES_NUMBER)
        self.assertEqual(v.country_code, VALID_VIES_COUNTRY_CODE)


class ModelTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_create(self):
        """Object is correctly created."""
        vies = VIESModel.objects.create(vat=VALID_VIES)
        self.assertNotEqual(VIESModel.objects.count(), 0)
        self.assertEqual(vies.vat, VALID_VIES)

    def test_save(self):
        """Object is correctly saved."""
        vies_saved = VIESModel()
        vies_saved.vat = VALID_VIES
        vies_saved.save()

        vies_received = VIESModel.objects.get(pk=vies_saved.pk)
        self.assertNotEqual(VIESModel.objects.count(), 0)
        self.assertEqual(vies_received.vat, VALID_VIES)


class ModelFormTestCase(unittest.TestCase):
    def test_is_valid(self):
        """Form is valid"""
        form = VIESModelForm({'vat_0': VALID_VIES_COUNTRY_CODE, 'vat_1': VALID_VIES_NUMBER})
        self.assertTrue(form.is_valid())

        vies = form.save()
        self.assertEqual(vies.vat, VALID_VIES)

    def test_is_not_valid_country(self):
        """Invalid country"""
        form = VIESModelForm({'vat_0': 'xx', 'vat_1': VALID_VIES_NUMBER})
        self.assertFalse(form.is_valid())

    def test_is_not_valid_numbers(self):
        """Invalid number"""
        form = VIESModelForm({'vat_0': VALID_VIES_COUNTRY_CODE, 'vat_1': 'xx123+-'})
        self.assertFalse(form.is_valid())

    def test_is_not_valid(self):
        """Invalid number"""
        form = VIESModelForm({'vat_0': 'GB', 'vat_1': '000000000'})
        self.assertFalse(form.is_valid())

    def test_save(self):
        """Form is saved"""
        form = VIESModelForm({'vat_0': VALID_VIES_COUNTRY_CODE, 'vat_1': VALID_VIES_NUMBER})
        self.assertTrue(form.is_valid())
        vies_saved = form.save()

        vies_received = VIESModel.objects.get(pk=vies_saved.pk)
        self.assertEqual(vies_received, vies_saved)
        self.assertNotEqual(VIESModel.objects.count(), 0)
        self.assertEqual(vies_received.vat, VALID_VIES)

    def test_empty(self):
        form = EmptyVIESModelForm({'name': 'Eva'})
        self.assertTrue(form.is_valid())