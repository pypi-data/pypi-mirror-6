"""Tests for the views of the dated_values app."""
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.timezone import now

from django_libs.tests.mixins import ViewTestMixin
from django_libs.tests.factories import UserFactory
from dateutil.relativedelta import relativedelta

from .factories import DatedValueTypeFactory
from ..models import DatedValue
from .. import settings as app_settings


class ValuesManagementViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``ValuesManagementView`` view class."""
    longMessage = True

    def get_view_kwargs(self):
        return {'ctype_id': self.ctype.id, 'object_id': self.user.id}

    def get_login_url(self):
        return settings.LOGIN_URL

    def get_view_name(self):
        return 'dated_values_management_view'

    def setUp(self):
        self.type1 = DatedValueTypeFactory()
        self.type2 = DatedValueTypeFactory()
        self.types = [self.type1, self.type2]
        self.user = UserFactory()
        self.staff = UserFactory(is_staff=True)
        self.superuser = UserFactory(is_superuser=True)
        self.ctype = ContentType.objects.get_for_model(User)
        self.data = {
            'date': (now() + relativedelta(days=30)).strftime(
                app_settings.DATE_FORMAT),
            'form-TOTAL_FORMS': u'2',
            'form-INITIAL_FORMS': u'2',
        }
        for i in range(0, 2):
            for j in range(0, 14):
                self.data.update({
                    'form-{0}-value{1}'.format(i, j): '{0}.12'.format(j)})

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(
            user=self.user,
            and_redirects_to=self.get_login_url() + '?next=/4/1/')
        self.should_be_callable_when_authenticated(self.staff)
        self.should_be_callable_when_authenticated(self.superuser)

        self.is_not_callable(
            kwargs={'ctype_id': self.ctype.id, 'object_id': 9001},
            message=('For an object, that does not exist, the view should not'
                     ' be callable.'))

        self.is_callable(method='post', data=self.data)
        self.assertEqual(DatedValue.objects.count(), 28, msg=(
            'When valid data is posted, there should be 14 new values in the'
            ' database.'))

        without_date = self.data.copy()
        without_date.pop('date')

        self.is_callable(method='post', data=without_date)
        self.assertEqual(DatedValue.objects.count(), 56, msg=(
            'When valid data is posted, there should be again 14 additional'
            ' values in the database.'))

        self.is_callable(method='post', data=without_date)
        self.assertEqual(DatedValue.objects.count(), 56, msg=(
            'When posting again with the same data, the amount of values in'
            ' the database should not have changed.'))

        self.type1.delete()
        self.type2.delete()
        self.is_not_callable(message=(
            'When there are no value types in the database, the view should'
            ' not be callable.'))
