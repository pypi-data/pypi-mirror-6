"""Tests for the models of the dated_values app."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import DatedValueFactory, DatedValueTypeFactory


class DatedValueTestCase(TestCase):
    """Tests for the ``DatedValue`` model class."""
    longMessage = True

    def setUp(self):
        self.datedvalue = DatedValueFactory()

    def test_instantiation(self):
        """Test instantiation of the ``DatedValue`` model."""
        self.assertTrue(self.datedvalue.pk)

    def test_properties(self):
        self.assertEqual(self.datedvalue.normal_value, Decimal('123.12'))
        self.datedvalue.normal_value = Decimal('12.34')
        self.assertEqual(self.datedvalue.value, Decimal('12.34'))
        self.assertEqual(
            self.datedvalue._ctype,
            ContentType.objects.get_for_model(User))

    def test_clean(self):
        self.assertRaises(ValidationError, self.datedvalue.clean)


class DatedValueTypeTestCase(TestCase):
    """Tests for the ``DatedValueType`` model class."""
    longMessage = True

    def setUp(self):
        self.datedvaluetype = DatedValueTypeFactory()

    def test_instantiation(self):
        """Test instantiation of the ``DatedValueType`` model."""
        self.assertTrue(self.datedvaluetype.pk)

    def test_clean(self):
        self.datedvaluetype.decimal_places = 9
        self.assertRaises(ValidationError, self.datedvaluetype.clean)
