"""Forms of the dated_values app."""
from decimal import Decimal
from django import forms
from django.utils.safestring import mark_safe

from dateutil.relativedelta import relativedelta

from .models import DatedValue
from . import settings


class ValuesForm(forms.Form):
    """Form to handle two weeks of DatedValue instances."""

    def __init__(self, obj, date, valuetype, index=None, *args, **kwargs):
        """
        :param obj: An object, that has values attached.
        :param date: A datetime date.
        :param valuetype: The DatedValueType, we are working on.
        :param instances: A queryset of DatedValues.

        """
        super(ValuesForm, self).__init__(*args, **kwargs)
        start = date - relativedelta(days=settings.DISPLAYED_ITEMS)
        end = date + relativedelta(days=settings.DISPLAYED_ITEMS * 2)
        values = DatedValue.objects.filter(
            type=valuetype, date__gte=start, object_id=obj.id,
            _ctype=valuetype.ctype, date__lt=end)
        self.valuetype = valuetype
        self.obj = obj
        self.instances = []
        for i in range(0, settings.DISPLAYED_ITEMS):
            current_date = date + relativedelta(days=i)
            self.fields['value{0}'.format(i)] = forms.DecimalField(
                required=False, decimal_places=self.valuetype.decimal_places,
                widget=forms.TextInput(attrs={
                    'class': 'dated-values-input value-active'}))
            try:
                instance = values.get(date=current_date)
            except DatedValue.DoesNotExist:
                self.instances.append(DatedValue(
                    type=valuetype, object_id=obj.id, date=current_date))
                self.initial['value{0}'.format(i)] = ''
            else:
                self.initial['value{0}'.format(i)] = instance.value
                self.instances.append(instance)

        # add hidden inputs for previous viewport to allow copying from there
        self.values_before = []
        for i in range(settings.DISPLAYED_ITEMS * -1, 0):
            current_date = date + relativedelta(days=i)
            try:
                instance = values.get(date=current_date)
            except DatedValue.DoesNotExist:
                value = ''
            else:
                value = instance.value.quantize(
                    Decimal(
                        '0' * 24 + '.' + '0' * self.valuetype.decimal_places))

            self.values_before.append(mark_safe(
                '<input type="hidden" class="value-before x{0} y{1}" '
                ' value="{2}" />'.format(
                    i + settings.DISPLAYED_ITEMS, index, value)))

        # add hidden inputs for next viewport to allow copying from there
        self.values_after = []
        for i in range(settings.DISPLAYED_ITEMS, settings.DISPLAYED_ITEMS * 2):
            current_date = date + relativedelta(days=i)
            try:
                instance = values.get(date=current_date)
            except DatedValue.DoesNotExist:
                value = ''
            else:
                value = instance.value.quantize(
                    Decimal(
                        '0' * 24 + '.' + '0' * self.valuetype.decimal_places))

            self.values_after.append(mark_safe(
                '<input type="hidden" class="value-after x{0} y{1}" '
                ' value="{2}" />'.format(
                    i - settings.DISPLAYED_ITEMS, index, value)))

    def save(self, **kwargs):
        saved_instances = []
        if self.prefix:
            prefix = self.prefix + '-'
        else:
            prefix = ''
        for i, instance in enumerate(self.instances):
            value = self.data.get('{0}value{1}'.format(prefix, i), None)
            if value:
                instance.value = value
                instance.save()
                saved_instances.append(instance)
            elif not value and instance.id is not None:
                instance.delete()
        return saved_instances


class MultiTypeValuesFormset(forms.formsets.formset_factory(ValuesForm)):
    def __init__(self, obj, date, valuetypes, *args, **kwargs):
        self.obj = obj
        self.date = date
        self.valuetypes = valuetypes
        self.extra = len(self.valuetypes)
        self.dates = [date + relativedelta(days=i) for i in range(
            0, settings.DISPLAYED_ITEMS)]
        self.next_viewport_start_date = date + relativedelta(
            days=settings.DISPLAYED_ITEMS)
        self.previous_viewport_start_date = date - relativedelta(
            days=settings.DISPLAYED_ITEMS)
        super(MultiTypeValuesFormset, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {
            'auto_id': self.auto_id,
            'prefix': self.add_prefix(i),
            'error_class': self.error_class,
            'obj': self.obj,
            'date': self.date,
            'valuetype': self.valuetypes[i],
            'index': i,
        }
        if self.is_bound:
            defaults['data'] = self.data
            defaults['files'] = self.files
        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
        defaults.update(kwargs)
        form = self.form(**defaults)
        self.add_fields(form, i)
        return form

    def save(self):
        saved_instances = []
        for form in self.forms:
            saved = form.save()
            if saved is not None:
                saved_instances.extend(saved)
        return saved_instances
