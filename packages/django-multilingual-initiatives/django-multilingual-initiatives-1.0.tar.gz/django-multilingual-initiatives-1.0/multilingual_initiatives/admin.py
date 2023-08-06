"""Admin classes for the ``multilingual_initiatives`` app."""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from hvad.admin import TranslatableAdmin

from .models import Initiative, InitiativePersonRole


class InitiativePersonRoleInline(admin.TabularInline):
    """Inline admin for ``InitiativePersonRole`` objects."""
    model = InitiativePersonRole


class InitiativeAdmin(TranslatableAdmin):
    """Admin for the ``Initiative`` model."""
    inlines = [InitiativePersonRoleInline]
    list_display = ['get_title', 'phone', 'website', 'start_date', 'end_date',
                    'description_short', 'organization', 'get_is_published']

    def get_title(self, obj):
        return obj.title
    get_title.short_description = _('Title')

    def get_is_published(self, obj):
        return obj.is_published
    get_is_published.short_description = _('Title')
    get_is_published.boolean = True

    def description_short(self, obj):
        if len(obj.description) > 40:
            return obj.description[:40]
        return obj.description
    description_short.short_description = _('Description')


admin.site.register(Initiative, InitiativeAdmin)
