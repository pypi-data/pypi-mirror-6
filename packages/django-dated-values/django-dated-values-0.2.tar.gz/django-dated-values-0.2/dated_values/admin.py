"""Admin classes for the dated_values app."""
from django.contrib import admin

from hvad.admin import TranslatableAdmin

from .models import DatedValue, DatedValueType


class DatedValueAdmin(admin.ModelAdmin):
    list_filter = ('type', )


admin.site.register(DatedValue, DatedValueAdmin)
admin.site.register(DatedValueType, TranslatableAdmin)
