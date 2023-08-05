# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core.xml import producers
from zope.interface import Interface

from ..interfaces import IMediaContent, IMediaContentVersion
from ..block import SlideshowBlock
from ..silvaxml import NS_MEDIACONTENT_URI


class MediaContentProducer(producers.SilvaVersionedContentProducer):
    grok.adapts(IMediaContent, Interface)

    def sax(self):
        self.startElementNS(
            NS_MEDIACONTENT_URI, 'mediacontent', {'id': self.context.id})
        self.sax_workflow()
        self.sax_versions()
        self.endElementNS(
            NS_MEDIACONTENT_URI, 'mediacontent')


class MediaContentVersionProducer(producers.SilvaProducer):
    grok.adapts(IMediaContentVersion, Interface)

    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        self.sax_metadata()
        url = self.context.get_external_url()
        if url:
            self.startElementNS(NS_MEDIACONTENT_URI, 'url')
            self.characters(url)
            self.endElementNS(NS_MEDIACONTENT_URI, 'url')
        asset = self.get_reference(u'asset')
        if asset is not None:
            self.startElementNS(NS_MEDIACONTENT_URI, 'asset')
            self.characters(asset)
            self.endElementNS(NS_MEDIACONTENT_URI, 'asset')
        link = self.get_reference(u'link')
        if link is not None:
            self.startElementNS(NS_MEDIACONTENT_URI, 'link')
            self.characters(link)
            self.endElementNS(NS_MEDIACONTENT_URI)
        self.endElement('content')


class SlideshowBlockProducer(producers.SilvaProducer):
    """Export SlideshowBlock to XML.
    """
    grok.adapts(SlideshowBlock, Interface)

    def sax(self, parent=None):
        self.startElementNS(
            NS_MEDIACONTENT_URI, 'slideshowblock',
            {'slideshow': parent.get_reference(self.context.identifier)})
        self.endElementNS(NS_MEDIACONTENT_URI, 'slideshowblock')
