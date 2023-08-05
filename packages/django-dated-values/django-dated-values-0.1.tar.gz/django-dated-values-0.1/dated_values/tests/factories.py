"""Factories for the dated_values app."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

import factory
from django_libs.tests.factories import HvadFactoryMixin, UserFactory

from ..models import DatedValue, DatedValueType


class DatedValueFactory(factory.DjangoModelFactory):
    """Factory for the ``DatedValue`` model."""
    FACTORY_FOR = DatedValue

    date = now()
    object = factory.LazyAttribute(lambda d: UserFactory())
    object_id = factory.LazyAttribute(lambda d: d.object.id)
    type = factory.SubFactory(
        'dated_values.tests.factories.DatedValueTypeFactory')
    value = Decimal('123.12345678')


class DatedValueTypeFactory(HvadFactoryMixin, factory.DjangoModelFactory):
    """Factory for the ``DatedValueType`` model."""
    FACTORY_FOR = DatedValueType

    ctype = ContentType.objects.get_for_model(User)
    name = factory.Sequence(lambda n: 'name {0}'.format(n))
    slug = factory.Sequence(lambda n: 'slug-{0}'.format(n))
