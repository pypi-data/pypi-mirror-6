from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import SoundCloud, COLORS

from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe


class SoundCloudPlugin(CMSPluginBase):
    model = SoundCloud
    name = _('SoundCloud')
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({'plugin_soundcloud': instance})
        return context

    def icon_src(self, instance):
        return instance.thumbnail_url

    def save_model(self, request, obj, form, change):
        obj.load_data()
        return super(SoundCloudPlugin, self).save_model(request, obj, form, change)

plugin_pool.register_plugin(SoundCloudPlugin)

