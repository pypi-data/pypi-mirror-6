"""Views for the dated_values app."""
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.timezone import datetime, now
from django.views.generic import FormView

from . import settings
from .decorators import permission_required
from .forms import MultiTypeValuesFormset
from .models import DatedValueType


def passes_test(user, obj):
    """
    Test method to pass for a user to get access.

    Superuser auto-passes test.

    """
    access_allowed = getattr(settings, 'ACCESS_ALLOWED')
    if user.is_superuser:
        return True
    return access_allowed(user, obj)


class ValuesManagementView(FormView):
    template_name = 'dated_values/values_management_form.html'
    form_class = MultiTypeValuesFormset

    def dispatch(self, request, *args, **kwargs):
        try:
            self.ctype = ContentType.objects.get_for_id(
                kwargs.get('ctype_id'))
            self.object = self.ctype.get_all_objects_for_this_type().get(
                pk=kwargs.get('object_id'))
        except ObjectDoesNotExist:
            raise Http404
        if passes_test(request.user, obj=self.object):
            self.valuetypes = DatedValueType.objects.filter(ctype=self.ctype)
            if len(self.valuetypes) == 0:
                raise Http404
            self.date_str = request.GET.get('date') or request.POST.get('date')
            if self.date_str:
                date_fmt = getattr(settings, 'DATE_FORMAT')
                self.date = datetime.strptime(self.date_str, date_fmt)
            else:
                self.date = now().date()
            return super(ValuesManagementView, self).dispatch(
                request, *args, **kwargs)
        return permission_required(super(ValuesManagementView, self).dispatch,
                                   test_to_pass=passes_test,
                                   obj=self.object)(
            request, *args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            form.save()
        return super(ValuesManagementView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ValuesManagementView, self).get_form_kwargs()
        kwargs.update({
            'obj': self.object,
            'date': self.date,
            'valuetypes': self.valuetypes,
        })
        return kwargs

    def get_success_url(self):
        if self.date_str:
            get_date = '?date={0}'.format(self.date_str)
        else:
            get_date = ''
        return reverse(
            'dated_values_management_view', kwargs=self.kwargs) + get_date
