# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

from zope.traversing.browser import absoluteURL
from zope.cachedescriptors.property import Lazy
from silva.core.layout.interfaces import ISilvaSkin
from silva.core import conf as silvaconf
from silva.core.layout.porto import porto
from silva.core.layout.porto.interfaces import IPorto
from silva.core.interfaces import IPublication, ISilvaObject


class ISilvaDocs(IPorto):
    """Layer for silva docs theme
    """
    silvaconf.resource('html5reset.css')
    silvaconf.resource('modernizr-1.7.min.js')
    silvaconf.resource('typography.css')
    silvaconf.resource('default.css')


class ISilvaDocsSkin(ISilvaDocs, ISilvaSkin):
    """Skin for silva docs theme
    """
    silvaconf.skin('Silva Docs')


silvaconf.layer(ISilvaDocs)


class Navigation(porto.Navigation):
    max_depth = 1


class Layout(porto.Layout):

    @Lazy
    def publication_title(self):
        return self.context.get_publication().get_title()

    @Lazy
    def publication_url(self):
        return self.context.get_publication().absolute_url()

    @Lazy
    def search_url(self):
        search = getattr(self.context, 'search', None)
        if ISilvaObject.providedBy(search):
            # get_silva_object cleanup the Acquisition path
            return absoluteURL(search.get_silva_object(), self.request)
        return None


class Favicon(porto.Favicon):
    """Declare that we have a favicon for this layer.

    Default favicon url is static/favicon.ico so we don't need to
    do anything besides declaring the Favicon viewlet inside this
    layer and have a static/favicon.ico file.
    If you want it to be something different, define a favicon_url property
    or method for this class.
    """
    pass


