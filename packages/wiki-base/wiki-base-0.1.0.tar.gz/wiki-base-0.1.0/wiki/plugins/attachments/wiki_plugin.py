# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext as _

from wiki.core.plugins import registry
from wiki.core.plugins.base import BasePlugin
from wiki.plugins.attachments import models
from wiki.plugins.attachments import settings
from wiki.plugins.attachments.markdown_extensions import AttachmentExtension


class AttachmentPlugin(BasePlugin):
    
    slug = settings.SLUG
    
    article_tab = (_(u'Attachments'), "icon-file")

    markdown_extensions = [AttachmentExtension()]
    
    def __init__(self):
        #print "I WAS LOADED!"
        pass
    
registry.register(AttachmentPlugin)

