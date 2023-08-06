"""Implementation of CMSPluginBase class for ``cmsplugin_link_extended``."""
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from djangocms_link.cms_plugins import LinkPlugin

from .models import LinkExtended


class ExtendedLinkPlugin(LinkPlugin):
    name = _('Link Extended')
    model = LinkExtended
    render_template = 'cmsplugin_link_extended/link.html'

    def render(self, context, instance, placeholder):
        context = super(ExtendedLinkPlugin, self).render(
            context, instance, placeholder)
        context.update({
            'css_classes': instance.css_classes,
        })
        return context


plugin_pool.register_plugin(ExtendedLinkPlugin)
