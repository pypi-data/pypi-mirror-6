# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

from zope.i18nmessageid import MessageFactory

from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from zeam.form import silva as silvaforms

from silva.core.conf.interfaces import ITitledContent
from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from Products.Silva.Publishable import NonPublishable
from Products.Silva import SilvaPermissions as perms
from silva.app.mediacontent.interfaces import (IEmbed,
    IEmbedFields)

_ = MessageFactory('silva')


class Embed(NonPublishable, SimpleItem):
    __doc__ = _('Embed html to include youtube videos ...')

    meta_type = 'Silva Embed'
    silvaconf.priority(1100)
    silvaconf.icon('embed.png')
    grok.implements(IEmbed)

    security = ClassSecurityInfo()

    # Fields
    _html = None

    security.declareProtected(perms.ChangeSilvaContent, 'set_html')
    def set_html(self, html):
        self._html = html
        return self._html

    security.declareProtected(perms.View, 'get_html')
    def get_html(self):
        return self._html


InitializeClass(Embed)


class EmbedView(silvaviews.View):
    """Default view to render an embed Embed video.
    """
    grok.context(IEmbed)

    def render(self):
        return self.context._html


class EmbedAddForm(silvaforms.SMIAddForm):
    """SMI add form for Silva Embed.
    """
    grok.context(IEmbed)
    grok.name(u'Silva Embed')
    fields = silvaforms.Fields(ITitledContent, IEmbedFields)


class EmbedEditForm(silvaforms.SMIEditForm):
    """SMI edit form for Silva Embed Video.
    """
    grok.context(IEmbed)
    fields = silvaforms.Fields(ITitledContent, IEmbedFields).omit('id')


