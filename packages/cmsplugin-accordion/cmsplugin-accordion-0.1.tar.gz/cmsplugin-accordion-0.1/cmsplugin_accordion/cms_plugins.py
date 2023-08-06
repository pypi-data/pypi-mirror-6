"""CMSPlugins for the cmsplugin_accordion app."""
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models


class AccordionPlugin(CMSPluginBase):
    model = models.AccordionPluginModel
    render_template = "cmsplugin_accordion/accordion_plugin.html"

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context


plugin_pool.register_plugin(AccordionPlugin)
