"""Admin classes for the cmsplugin_accordion app."""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from cms.admin.placeholderadmin import PlaceholderAdmin

from . import models


# MODEL ADMINS ================================================================
# =============================================================================
class AccordionAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    search_fields = ['name', ]


class AccordionRowAdmin(PlaceholderAdmin):
    list_display = ['title', 'accordion__name', 'position', ]
    list_editable = ['position', ]
    list_filter = ['accordion', ]
    search_fields = ['title', 'accordion__name', ]

    def accordion__name(self, obj):
        return obj.accordion.name
    accordion__name.short_description = _('Accordion')


admin.site.register(models.Accordion, AccordionAdmin)
admin.site.register(models.AccordionRow, AccordionRowAdmin)
