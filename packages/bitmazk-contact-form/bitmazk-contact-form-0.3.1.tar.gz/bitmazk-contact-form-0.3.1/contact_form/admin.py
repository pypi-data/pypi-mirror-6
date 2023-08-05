"""Admins for the ``contact_form`` app."""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from hvad.admin import TranslatableAdmin

from .models import ContactFormCategory


class ContactFormCategoryAdmin(TranslatableAdmin):
    """Admin for the ``ContactFormCategory`` model."""
    list_display = ['transname', 'slug', 'all_translations']

    def transname(self, obj):
        # somehow this works though just adding name to the list_display is
        # officially not supported
        return obj.name
    transname.short_description = _('Name')


admin.site.register(ContactFormCategory, ContactFormCategoryAdmin)
