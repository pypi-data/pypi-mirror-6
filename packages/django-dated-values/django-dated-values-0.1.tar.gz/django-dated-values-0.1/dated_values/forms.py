"""Forms of the dated_values app."""
from django import forms

from dateutil.relativedelta import relativedelta

from .models import DatedValue
from . import settings


class ValuesForm(forms.Form):
    """Form to handle two weeks of DatedValue instances."""

    def __init__(self, obj, date, valuetype, *args, **kwargs):
        """
        :param obj: An object, that has values attached.
        :param date: A datetime date.
        :param valuetype: The DatedValueType, we are working on.
        :param instances: A queryset of DatedValues.

        """
        super(ValuesForm, self).__init__(*args, **kwargs)
        values = DatedValue.objects.filter(
            type=valuetype, date__gte=date,
            date__lt=date + relativedelta(days=settings.DISPLAYED_ITEMS))
        self.valuetype = valuetype
        self.obj = obj
        self.instances = []
        for i in range(0, settings.DISPLAYED_ITEMS):
            current_date = date + relativedelta(days=i)
            self.fields['value{0}'.format(i)] = forms.DecimalField(
                required=False, decimal_places=self.valuetype.decimal_places,
                widget=forms.TextInput(attrs={'class': 'dated-values-input'}))
            try:
                instance = values.get(date=current_date)
            except DatedValue.DoesNotExist:
                self.instances.append(DatedValue(
                    type=valuetype, object_id=obj.id, date=current_date))
                self.initial['value{0}'.format(i)] = ''
            else:
                self.initial['value{0}'.format(i)] = instance.value
                self.instances.append(instance)

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
        self.extra = 2
        self.obj = obj
        self.date = date
        self.valuetypes = valuetypes
        self.dates = [date + relativedelta(days=i) for i in range(
            0, settings.DISPLAYED_ITEMS)]
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
