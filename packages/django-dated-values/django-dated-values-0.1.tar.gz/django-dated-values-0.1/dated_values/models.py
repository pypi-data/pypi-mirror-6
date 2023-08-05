"""Just an empty models file to let the testrunner recognize this as app."""
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from hvad.models import TranslatableModel, TranslatedFields


class DatedValue(models.Model):
    """
    The value, that is attached to an object for a given date.

    :_ctype: Will always be the same ctype as the type has.
    :date: The optional date, when this value applies.
    :object: The related object.
    :object_id: The id of the object, that this value is for.
    :type: The DatedValueType this value belongs to.
    :value: The decimal value, that is attached.

    """
    _ctype = models.ForeignKey(
        ContentType,
        verbose_name=_('Content Type'),
    )

    date = models.DateField(
        verbose_name=_('Date'),
        blank=True, null=True,
    )

    object = generic.GenericForeignKey(
        ct_field='_ctype',
        fk_field='object_id',
    )

    object_id = models.PositiveIntegerField(
        verbose_name=_('Object id'),
    )

    type = models.ForeignKey(
        'dated_values.DatedValueType',
        verbose_name=_('Type'),
    )

    value = models.DecimalField(
        verbose_name=_('Value'),
        max_digits=24,
        decimal_places=8,
    )

    def __unicode__(self):
        return '{0}: {1}'.format(self.type, self.normal_value)

    def clean(self):
        if self.value and len(self.value.to_eng_string().split(
                '.')[1]) > self.type.decimal_places:
            raise ValidationError(_(
                'The value can only have {0} decimal places.'.format(
                    self.type.decimal_places)))

    @property
    def normal_value(self):
        """
        Returns the normalized value according to the settings in the type.

        """
        if self.value:
            return getattr(self, 'value').quantize(Decimal(
                '0' * 24 + '.' + '0' * self.type.decimal_places))

    @normal_value.setter
    def normal_value(self, value):
        setattr(self, 'value', value)

    def save(self, *args, **kwargs):
        self._ctype = self.type.ctype
        super(DatedValue, self).save(*args, **kwargs)


class DatedValueType(TranslatableModel):
    """
    The type of a dated value and what model type it belongs to.

    :ctype: The ctype of the related model.
    :decimal_places: If you want to limit the decimal places, that the
      ``normal_value`` attribute outputs, you can specify an alternative here.
      Defaults to 2.
    :slug: A unique identifier.

    translated:
    :name: A displayable name for the value type.

    """
    ctype = models.ForeignKey(
        ContentType,
        verbose_name=_('Content Type'),
    )

    decimal_places = models.PositiveIntegerField(
        verbose_name=_('Decimal places'),
        default=2,
    )

    slug = models.SlugField(
        verbose_name=_('Slug'),
        max_length=64,
        unique=True,
    )

    translations = TranslatedFields(
        name=models.CharField(
            verbose_name=_('Name'),
            max_length=256,
        )
    )

    def __unicode__(self):
        return '{0} ({1})'.format(
            self.safe_translation_getter('name', self.slug), self.ctype)

    def clean(self):
        if self.decimal_places > 8:
            raise ValidationError(_(
                'decimal_places cannot be bigger than 8.'))
