# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# $Id$

from zope.cachedescriptors.property import CachedProperty

from silva.core.layout.interfaces import ISilvaSkin
from silva.core.layout.porto.interfaces import IPorto
from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews

class IMultiflex(IPorto):
    """Multiflex layer to include CSS
    """

    silvaconf.resource('layout_setup.css')
    silvaconf.resource('layout_text.css')


class IMultiflexSkin(IMultiflex, ISilvaSkin):
    """Skin Multiflex.
    """

    silvaconf.skin('Multiflex')


silvaconf.layer(IMultiflex)

class Layout(silvaviews.ContentProvider):

    @CachedProperty
    def publication_title(self):
        return self.context.get_publication().get_title()

    @CachedProperty
    def publication_url(self):
        return self.context.get_publication().absolute_url()

