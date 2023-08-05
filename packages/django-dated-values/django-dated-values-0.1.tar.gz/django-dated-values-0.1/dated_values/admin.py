"""Admin classes for the dated_values app."""
from django.contrib import admin

from hvad.admin import TranslatableAdmin

from .models import DatedValue, DatedValueType


admin.site.register(DatedValue)
admin.site.register(DatedValueType, TranslatableAdmin)
