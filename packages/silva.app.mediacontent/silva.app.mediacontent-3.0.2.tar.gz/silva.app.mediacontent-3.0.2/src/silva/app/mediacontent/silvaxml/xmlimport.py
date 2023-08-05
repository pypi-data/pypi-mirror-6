# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

from zope.publisher.browser import TestRequest
from zeam.component import getWrapper

from silva.app.mediacontent.block import SlideshowBlock
from silva.app.mediacontent.silvaxml import NS_MEDIACONTENT_URI
from silva.core import conf as silvaconf
from silva.core.contentlayout.silvaxml.xmlimport import BlockHandler
from silva.core.xml import NS_SILVA_URI, handlers
from silva.core.contentlayout.interfaces import IBlockController

silvaconf.namespace(NS_MEDIACONTENT_URI)


class MediaContentHandler(handlers.SilvaHandler):
    silvaconf.name('mediacontent')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): MediaContentVersionHandler}

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['silva.app.mediacontent']
        factory.manage_addMediaContent(identifier, '', no_default_version=True)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_MEDIACONTENT_URI, 'mediacontent'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_MEDIACONTENT_URI, 'mediacontent'):
            self.notifyImport()


class MediaContentVersionHandler(handlers.SilvaVersionHandler):

    def getOverrides(self):
        return {
            (NS_MEDIACONTENT_URI, 'url'):
                self.handlerFactories.contentHandler('url'),
            (NS_MEDIACONTENT_URI, 'asset'):
                self.handlerFactories.contentHandler('asset'),
            (NS_MEDIACONTENT_URI, 'link'):
                self.handlerFactories.contentHandler('link')}

    def _createVersion(self, identifier):
        factory = self.parent().manage_addProduct['silva.app.mediacontent']
        factory.manage_addMediaContentVersion(identifier, '')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'content'):
            self.createVersion(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'content'):
            importer = self.getExtra()
            version = self.result()
            url = self.getData('url')
            if url is not None:
                version.set_external_url(url)
            link = self.getData('link')
            if link is not None:
                importer.resolveImportedPath(version, version.set_link, link)
            asset = self.getData('asset')
            if asset is not None:
                importer.resolveImportedPath(version, version.set_asset, asset)
            self.updateVersionCount()
            self.storeMetadata()
            self.storeWorkflow()


class AgendaInfoBlockHandler(BlockHandler):
    silvaconf.name('agendainfoblock')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_MEDIACONTENT_URI, 'slideshowblock'):
            path = attrs[(None, 'slideshow')]
            block = SlideshowBlock()
            page = self.parentHandler().parent()
            importer = self.getExtra()
            self._block = block

            def set_target(target):
                controller = getWrapper(
                    (block, page, TestRequest()),
                    IBlockController)
                controller.content = target

            importer.resolveImportedPath(page, set_target, path)
            self._block = block

    def endElementNS(self, name, qname):
        if name == (NS_MEDIACONTENT_URI, 'slideshowblock'):
            self.add_block(self._block)
            self._block = None

