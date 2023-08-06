"""Admin classes for the ``multilingual_orgs`` app."""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from hvad.admin import TranslatableAdmin

from .models import Organization, OrganizationPersonRole


class OrganizationPersonRoleInline(admin.TabularInline):
    """Inline admin for ``OrganizationPersonRole`` objects."""
    model = OrganizationPersonRole


class OrganizationAdmin(TranslatableAdmin):
    """Admin for the ``Organization`` model."""
    inlines = [OrganizationPersonRoleInline]
    list_display = ['get_title', 'phone', 'website', 'get_is_published']

    def get_title(self, obj):
        return obj.title
    get_title.short_description = _('Title')

    def get_is_published(self, obj):
        return obj.is_published
    get_is_published.short_description = _('Is published')
    get_is_published.boolean = True


admin.site.register(Organization, OrganizationAdmin)
