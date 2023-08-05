"""Just an empty models file to let the testrunner recognize this as app."""
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import get_language, ugettext_lazy as _

from hvad.descriptors import LanguageCodeAttribute, TranslatedAttribute
from hvad.models import TranslatableModel, TranslatedFields


# When using the TranslatableModel class, it still uses the default Django
# related manager for some reason instead of the translation aware one. It
# therefore returns only the untranslated/sharded model instance. When you
# then call a custom descriptor, the descriptor itself will query for the
# translation. Unfortunately the used querying method is fairly simple and if
# there is no object for this language, we get no results. With this update,
# we instead of showing nothing retrieve the english version as fallback,
# since it is always the first to be created.

class BetterTranslatedAttribute(TranslatedAttribute):
    """
    Customized TranslatedAttribute so that we fetch the english variant of the
    attribute if the requested translation does not exist.

    Basic translated attribute descriptor.

    Proxies attributes from the shared instance to the translated instance.

    """
    def translation(self, instance):  # pragma: nocover

        def get_translation(instance, language_code=None):
            opts = instance._meta
            if not language_code:
                language_code = get_language()
            accessor = getattr(instance, opts.translations_accessor)
            try:
                return accessor.get(language_code=language_code)
            except ObjectDoesNotExist:
                # doing a fallback in case the requested language doesn't exist
                return accessor.get(language_code='en')

        cached = getattr(instance, self.opts.translations_cache, None)
        if not cached:
            cached = get_translation(instance)
            setattr(instance, self.opts.translations_cache, cached)
        return cached


class BetterTranslatedAttributeMixin(object):

    @classmethod
    def contribute_translations(cls, rel):
        """
        Contribute translations options to the inner Meta class and set the
        descriptors.

        This get's called from TranslatableModelBase.__new__
        """
        opts = cls._meta
        opts.translations_accessor = rel.get_accessor_name()
        opts.translations_model = rel.model
        opts.translations_cache = '%s_cache' % rel.get_accessor_name()
        trans_opts = opts.translations_model._meta

        # Set descriptors
        ignore_fields = [
            'pk',
            'master',
            opts.translations_model._meta.pk.name,
        ]
        for field in trans_opts.fields:
            if field.name in ignore_fields:
                continue
            if field.name == 'language_code':
                attr = LanguageCodeAttribute(opts)
            else:
                attr = BetterTranslatedAttribute(opts, field.name)
            setattr(cls, field.name, attr)


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
        return '[{0}] {1} ({2}): {3}'.format(
            self.date, self.object, self.type, self.normal_value)

    def clean(self):
        if self.value:
            split_value = self.value.to_eng_string().split('.')
            if len(split_value) > 1 and len(
                    split_value[1]) > self.type.decimal_places:
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

    class Meta:
        ordering = ['date', ]


class DatedValueType(BetterTranslatedAttributeMixin, TranslatableModel):
    """
    The type of a dated value and what model type it belongs to.

    :ctype: The ctype of the related model.
    :decimal_places: If you want to limit the decimal places, that the
      ``normal_value`` attribute outputs, you can specify an alternative here.
      Defaults to 2.
    :editable: True, if the valuetype is editable by an admin. False will only
      display them.
    :hidden: True, if the type should not at all be displayed on the management
      page.
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

    editable = models.BooleanField(
        verbose_name=_('Editable'),
        default=True,
    )

    hidden = models.BooleanField(
        verbose_name=_('Hidden'),
        default=False,
    )

    def __unicode__(self):
        return '{0} ({1})'.format(
            self.safe_translation_getter('name', self.slug), self.ctype)

    def clean(self):
        if self.decimal_places > 8:
            raise ValidationError(_(
                'decimal_places cannot be bigger than 8.'))
