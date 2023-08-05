# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.traversing.browser import absoluteURL
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from silva.app.page.interfaces import IPage
from silva.core import conf as silvaconf
from silva.core.contentlayout import Design, Slot
from silva.core.contentlayout.slots import restrictions
from silva.core.interfaces import IPublication, IImage
from silva.core.layout.interfaces import ICustomizableTag
from silva.core.layout.porto import porto
from silva.fanstatic import need
from silva.translations import translate as _
from silvatheme.standardissue.standardissue import IStandardIssue

grok.templatedir('templates')


class IAdvancedTemplate(ICustomizableTag):
    """Advanced layout template for Page
    """
    silvaconf.only_for(IPage)


class IAdvancedResources(IDefaultBrowserLayer):
    silvaconf.resource('advanced.css')


class AdvancedDesign(Design):
    grok.order(5)
    grok.name('demo.advanced_template')
    grok.title(_(u"Advanced design (StandardIssue)"))

    description = _(u'A design that uses a section from a layout')

    markers = [IAdvancedTemplate]

    slots = {
        'one': Slot(
            restrictions=[
                restrictions.CodeSourceName(allowed=['cs_toc'])]),
        'two': Slot(
            restrictions=[
                restrictions.CodeSourceName(disallowed=['cs_toc']),
                restrictions.Content(IImage),
                restrictions.BlockAll()]),
        'navigation': Slot(
            tag='nav',
            restrictions=[
                restrictions.CodeSourceName(allowed=['cs_toc']),
                restrictions.BlockAll()]),
        'footer': Slot(tag='footer', css_class="horizontal-blocks")}

    def update(self):
        self.root = self.content.get_publication()
        need(IAdvancedResources)

    def top_menu_items(self):
        for content in self.root.get_ordered_publishables():
            if not IPublication.providedBy(content):
                continue
            yield {'title': content.get_title_or_id(),
                   'css': content in self.request.PARENTS and 'active' or '',
                   'url': absoluteURL(content, self.request)}


class AdvancedLayout(porto.Layout):
    grok.context(IAdvancedTemplate)
    grok.layer(IStandardIssue)
    grok.name('layout')
