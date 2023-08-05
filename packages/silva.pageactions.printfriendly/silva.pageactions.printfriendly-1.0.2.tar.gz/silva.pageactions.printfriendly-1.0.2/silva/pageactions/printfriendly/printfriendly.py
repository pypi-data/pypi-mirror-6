# -*- coding: utf-8 -*-
# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.layout.interfaces import ISilvaLayer, ISilvaSkin
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IHTTPResponseHeaders
from silva.pageactions.base.base import PageAction

from five import grok
from zope import component
from zope.publisher.browser import applySkin


class IPrintLayer(ISilvaLayer):
    pass


class IPrintSkin(IPrintLayer, ISilvaSkin):
    pass


class PrintFriendly(silvaviews.View):

    grok.name('print.html')

    def update(self):
        component.getMultiAdapter(
            (self.context, self.request), IHTTPResponseHeaders)()
        applySkin(self.request, IPrintSkin)


class PrintAction(PageAction):

    grok.order(20)

