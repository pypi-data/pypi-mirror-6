# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import uuid

from five import grok
from grokcore.chameleon.components import ChameleonPageTemplate
from zope.component import getUtility
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.http import IHTTPRequest

import js.jquery

from silva.core import conf as silvaconf
from silva.core.contentlayout.blocks import Block, BlockController
from silva.core.contentlayout.interfaces import IPage
from silva.core.interfaces import IContainer, IImage
from silva.core.references.reference import Reference
from silva.core.references.interfaces import IReferenceService
from silva.fanstatic import need
from silva.translations import translate as _
from silva.app.mediacontent.interfaces import IMediaContent
from zeam.form import silva as silvaforms


class SlideshowBlock(Block):
    grok.name('media-slideshow')
    grok.title('Media content slideshow')
    grok.order(20)
    silvaconf.icon('mediacontent.png')

    def __init__(self, identifier=None):
        if identifier is None:
            identifier = unicode(uuid.uuid1())
        self.identifier = identifier


class ISlideshowResources(IDefaultBrowserLayer):
    silvaconf.resource(js.jquery.jquery)
    silvaconf.resource('slideshow.js')
    silvaconf.resource('slideshow.css')


class SlideshowRender(object):
    template = ChameleonPageTemplate(filename='slideshow.cpt')

    def __init__(self, container, request):
        self.container = container
        self.request = request

    def default_namespace(self):
         return {'request': self.request,
                 'context': self.container,
                 'view': self}

    def namespace(self):
        return {}

    def update(self):
        need(ISlideshowResources)
        self.contents = []
        for content in self.container.get_ordered_publishables(IMediaContent):
            version = content.get_viewable()
            if version is None:
                continue
            info = {
                'title': version.get_title(),
                'text': version.get_text().strip(),
                'image': None}
            asset = version.get_asset()
            if IImage.providedBy(asset):
                dimensions = asset.get_dimensions()
                info.update({
                        'image': asset.url(request=self.request),
                        'width': dimensions.width,
                        'height': dimensions.height
                        })
            self.contents.append(info)

    def __call__(self):
        self.update()
        return self.template.render(self)


class SlideshowBlockController(BlockController):
     grok.adapts(SlideshowBlock, Interface, IHTTPRequest)

     def __init__(self, block, context, request):
        super(SlideshowBlockController, self).__init__(block, context, request)
        self._name = block.identifier
        self._service = getUtility(IReferenceService)

     def editable(self):
         return True

     @apply
     def container():

         def getter(self):
             reference = self._service.get_reference(
                 self.context, name=self._name)
             if reference is not None:
                 return reference.target
             return None

         def setter(self, value):
             reference = self._service.get_reference(
                 self.context, name=self._name, add=True)
             if isinstance(value, int):
                 reference.set_target_id(value)
             else:
                 reference.set_target(value)

         return property(getter, setter)

     def remove(self):
         self._service.delete_reference(self.context, name=self._name)

     def render(self, view=None):
         return SlideshowRender(self.container, self.request)()


class ISlideshowFields(Interface):
    container = Reference(
        IContainer,
        title=u"Container with media content",
        description=u"Container where the media content items are",
        required=True)


class AddSlideshowBlockAction(silvaforms.Action):
    grok.implements(
        silvaforms.IDefaultAction,
        silvaforms.IRESTExtraPayloadProvider,
        silvaforms.IRESTCloseOnSuccessAction)
    title = _('Add')

    def get_extra_payload(self, form):
        adding = form.__parent__
        if adding.block_id is None:
            return {}
        return {
            'block_id': adding.block_id,
            'block_data': adding.block_controller.render(),
            'block_editable': True}

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return silvaforms.FAILURE
        adding = form.__parent__
        adding.add(SlideshowBlock()).container = data['container']
        notify(ObjectModifiedEvent(form.context))
        form.send_message(_(u"New slideshow component added."))
        return silvaforms.SUCCESS


class AddSlideshowBlock(silvaforms.RESTPopupForm):
     grok.adapts(SlideshowBlock, IPage)
     grok.name('add')

     label = u'Add a slideshow'
     fields = silvaforms.Fields(ISlideshowFields)
     actions = silvaforms.Actions(
         silvaforms.CancelAction(),
         AddSlideshowBlockAction())

     def __init__(self, context, request, configuration, restrictions):
         super(AddSlideshowBlock, self).__init__(context, request)
         self.restrictions = restrictions
         self.configuration = configuration


class EditSlideshowBlockAction(silvaforms.Action):
    grok.implements(
        silvaforms.IDefaultAction,
        silvaforms.IRESTExtraPayloadProvider,
        silvaforms.IRESTCloseOnSuccessAction)
    title = _('Save changes')

    def get_extra_payload(self, form):
        # This is kind of an hack, but the name of the form is the block id.
        return {
            'block_id': form.__name__,
            'block_data': form.getContent().render(),
            'block_editable': True}

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return silvaforms.FAILURE
        manager = form.getContentData()
        manager.set('container', data.getWithDefault('container'))
        form.send_message(_(u"Slideshow component modified."))
        notify(ObjectModifiedEvent(form.context))
        return silvaforms.SUCCESS


class EditSlideshowBlock(silvaforms.RESTPopupForm):
     grok.adapts(SlideshowBlock, IPage)
     grok.name('edit')

     label = u'Edit a slideshow'
     fields = silvaforms.Fields(ISlideshowFields)
     actions = silvaforms.Actions(
         silvaforms.CancelAction(),
         EditSlideshowBlockAction())
     ignoreContent = False

     def __init__(self, block, context, request, controller, restrictions):
         super(EditSlideshowBlock, self).__init__(context, request)
         self.restrictions = restrictions
         self.block = block
         self.setContentData(controller)
