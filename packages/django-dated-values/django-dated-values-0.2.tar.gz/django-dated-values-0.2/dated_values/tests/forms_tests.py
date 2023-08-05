"""Tests for the forms of the dated_values app."""
from django.test import TestCase
from django.utils.timezone import now

from django_libs.tests.factories import UserFactory

from ..forms import ValuesForm, MultiTypeValuesFormset
from ..models import DatedValue
from .factories import DatedValueTypeFactory


class ValuesFormTestCase(TestCase):
    """Tests for the most basic ValuesForm."""
    longMessage = True

    def setUp(self):
        self.data = {}
        for i in range(0, 14):
            self.data.update({'value{0}'.format(i): '{0}.12'.format(i)})
        self.user = UserFactory()
        self.type = DatedValueTypeFactory()

    def test_form(self):
        # test instantiation
        form = ValuesForm(self.user, now(), self.type)

        # Tests for creating objects
        form = ValuesForm(self.user, now(), self.type, data=self.data)
        self.assertTrue(form.is_valid(), msg=(
            'The form should be valid. Errors: {0}'.format(form.errors)))
        form.save()
        self.assertEqual(DatedValue.objects.count(), 14, msg=(
            'After calling save, there are not the correct amount of dated'
            ' values in the database.'))

        form = ValuesForm(self.user, now(), self.type, data=self.data)
        self.assertTrue(form.is_valid(), msg=(
            'The form should be valid. Errors: {0}'.format(form.errors)))

        form.save()
        self.assertEqual(DatedValue.objects.count(), 14, msg=(
            'After calling save with an instances in the database, there was'
            ' not the correct amount of dated values in the database.'))

        # Tests for not creating and deleting objects
        data = self.data.copy()
        data.update({'value1': ''})
        form = ValuesForm(self.user, now(), self.type, data=data)
        self.assertTrue(form.is_valid(), msg=(
            'The form with instance should be valid with the blank value.'
            ' Errors: {0}'.format(form.errors)))

        form.save()
        self.assertEqual(DatedValue.objects.count(), 13, msg=(
            'After calling save with an empty value and an instance, the form'
            ' should have deleted that instance.'))

        data = self.data.copy()
        data.update({'value1': ''})
        form = ValuesForm(self.user, now(), self.type, data=data)
        self.assertTrue(form.is_valid(), msg=(
            'The form should be valid even with the value being blank.'
            ' Errors: {0}'.format(form.errors)))

        form.save()
        self.assertEqual(DatedValue.objects.count(), 13, msg=(
            'After calling save, there are not the correct amount of dated'
            ' values in the database.'))


class MultiTypeValuesFormsetTestCase(TestCase):
    """Tests for the MultiTypeValuesFormset formset class."""
    longMessage = True

    def setUp(self):
        self.type1 = DatedValueTypeFactory()
        self.type2 = DatedValueTypeFactory()
        self.types = [self.type1, self.type2]
        self.user = UserFactory()
        self.data = {
            'form-TOTAL_FORMS': u'2',
            'form-INITIAL_FORMS': u'2',
        }
        for i in range(0, 2):
            for j in range(0, 14):
                self.data.update({
                    'form-{0}-value{1}'.format(i, j): '{0}.12'.format(j)})

    def test_form(self):
        # test form instantiation
        form = MultiTypeValuesFormset(self.user, now(), self.types)

        # Tests for creating objects
        form = MultiTypeValuesFormset(self.user, now(), self.types,
                                      data=self.data)
        self.assertTrue(form.is_valid(), msg=(
            'The form should be valid. Errors: {0}'.format(form.errors)))
        form.save()
        self.assertEqual(DatedValue.objects.count(), 28, msg=(
            'After calling save, there are not the correct amount of dated'
            ' values in the database.'))

        form = MultiTypeValuesFormset(self.user, now(), self.types,
                                      data=self.data)
        self.assertTrue(form.is_valid(), msg=(
            'The form should be valid. Errors: {0}'.format(form.errors)))

        form.save()
        self.assertEqual(DatedValue.objects.count(), 28, msg=(
            'After calling save on the form, where we have instances in the'
            ' database, there should still be the same instances in the'
            ' database.'))

        # Tests for not creating and deleting objects
        data = self.data.copy()
        data.update({
            'form-0-value1': '',
            'form-1-value1': '',
        })
        form = MultiTypeValuesFormset(self.user, now(), self.types,
                                      data=data)
        self.assertTrue(form.is_valid(), msg=(
            'The form should be valid with the blank values.'
            ' Errors: {0}'.format(form.errors)))

        form.save()
        self.assertEqual(DatedValue.objects.count(), 26, msg=(
            'After calling save on the formset with 4 empty values and'
            ' persistent values in th database, there should be a decreased'
            ' amount of values in the database.'))

        form = MultiTypeValuesFormset(self.user, now(), self.types,
                                      data=data)
        self.assertTrue(form.is_valid(), msg=(
            'The form should be valid even with some values being blank.'
            ' Errors: {0}'.format(form.errors)))

        form.save()
        self.assertEqual(DatedValue.objects.count(), 26, msg=(
            'When we call save again with the same data, there should be'
            ' the same amount of values in the database.'))

        # Tests for invalid data
        data = self.data.copy()
        data.update({
            'form-0-value1': '12.012312',
        })
        form = MultiTypeValuesFormset(self.user, now(), self.types,
                                      data=data)
        self.assertFalse(form.is_valid(), msg='The form should not be valid.')
