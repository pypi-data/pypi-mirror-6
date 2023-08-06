import re
from django.db import models
from .settings import *
from django.conf import settings
from django.template import Template
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin

from json import load
from urllib import urlencode
from urllib2 import urlopen
from urlparse import urlsplit, urlunsplit, parse_qsl



# use CMSPLUGIN_SOUNDCLOUD_COLORS to override COLORS
COLORS = getattr(settings, 'CMSPLUGIN_SOUNDCLOUD_COLORS',
                            CMSPLUGIN_SOUNDCLOUD_COLORS)

# use CMSPLUGIN_SOUNDCLOUD_HEIGHTS to override HEIGHTS
HEIGHTS = getattr(settings, 'CMSPLUGIN_SOUNDCLOUD_HEIGHTS',
                            CMSPLUGIN_SOUNDCLOUD_HEIGHTS)


OEMBED_URL_FORMAT = 'http://soundcloud.com/oembed?url=%s&format=json'


class SoundCloud(CMSPlugin):
    url           = models.CharField(_('Sound Cloud URL'), max_length=255,
                        help_text=_('(i. e. https://soundcloud.com/band/song)'))
    author_name   = models.CharField(max_length=255, editable=False)
    author_url    = models.CharField(max_length=255, editable=False)
    title         = models.CharField(max_length=255, editable=False)
    description   = models.CharField(max_length=255, editable=False)
    thumbnail_url = models.CharField(max_length=255, editable=False)
    color         = models.CharField(_('Color'), max_length=6, choices=COLORS,
                        default=COLORS[0][0],
                        help_text=_('Main color of the widget.'))
    auto_play     = models.BooleanField(_('Play automatically'))
    show_artwork  = models.BooleanField(_('Show artwork'))
    hide_related  = models.BooleanField(_('Hide related'))
    visual        = models.BooleanField(_('Visual mode'))
    height        = models.IntegerField(_('Height'), choices=HEIGHTS,
                        default=HEIGHTS[0][0],
                        help_text=_('Height of widhte in visual mode.'))
    src           = models.TextField(editable=False)

    render_template = 'cmsplugin_soundcloud.html'

    def __unicode__(self):
        return self.title

    def load_data(self, *args, **kwargs):
        properties         = load(urlopen(OEMBED_URL_FORMAT % self.url))
        self.author_name   = properties['author_name']
        self.author_url    = properties['author_url']
        self.title         = properties['title']
        self.description   = properties['description']
        self.thumbnail_url = properties['thumbnail_url']
        if not self.visual:
            self.height    = 166
        url = urlsplit(re.findall(r'src="([^"]*)"', properties['html'])[0])
        qs  = dict(parse_qsl(url.query))
        qs['color']        = self.color
        qs['auto_play']    = self.auto_play    and 'true' or 'false'
        qs['show_artwork'] = self.show_artwork and 'true' or 'false'
        qs['hide_related'] = self.hide_related and 'true' or 'false'
        qs['visual']       = self.visual       and 'true' or 'false'
        self.src = urlunsplit((url.scheme, url.netloc, url.path, urlencode(qs), url.fragment))

