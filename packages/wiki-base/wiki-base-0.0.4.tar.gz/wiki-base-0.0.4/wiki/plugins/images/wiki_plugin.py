# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

from wiki.core.plugins import registry
from wiki.core.plugins.base import BasePlugin
from wiki.plugins.images import models, settings, forms
from wiki.plugins.images.markdown_extensions import ImageExtension

class ImagePlugin(BasePlugin):
    
    slug = settings.SLUG
    sidebar = {
        'headline': _('Images'),
        'icon_class': 'icon-picture',
        'template': 'wiki/plugins/images/sidebar.html',
        'form_class': forms.SidebarForm,
        'get_form_kwargs': (lambda a: {'instance': models.Image(article=a)})
    }
    

    class RenderMedia:
        js = [
            'wiki/colorbox/jquery.colorbox-min.js',
            'wiki/js/images.js',
        ]
        
        css = {
            'screen': 'wiki/colorbox/example1/colorbox.css'
        }

    markdown_extensions = [ImageExtension()]
    
    def __init__(self):
        #print "I WAS LOADED!"
        pass
    
registry.register(ImagePlugin)

