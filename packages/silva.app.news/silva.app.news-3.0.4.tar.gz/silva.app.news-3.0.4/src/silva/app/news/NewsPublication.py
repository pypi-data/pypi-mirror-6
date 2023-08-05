# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from five import grok
from zope.component import getUtility

from Products.Silva.Publication import Publication
from Products.Silva.Folder.addables import AddableContents
from Products.Silva.cataloging import CatalogingAttributes

from silva.core import conf as silvaconf
from silva.core.interfaces import IAsset, IAddableContents
from silva.core.interfaces.events import IContentCreatedEvent
from silva.core.services.interfaces import IMetadataService
from zeam.form import silva as silvaforms

from .interfaces import INewsPublication, INewsItemContent, INewsItemFilter
from .interfaces import INewsViewer, IServiceNewsCategorization



class NewsPublication(Publication):
    """A special publication type (a.k.a. News Source) for news
    and agenda items. News Filters and Agenda Filters can pick up
    news from these sources anywhere in a Silva site.
    """
    security = ClassSecurityInfo()

    grok.implements(INewsPublication)
    meta_type = "Silva News Publication"
    silvaconf.icon("www/news_source.png")
    silvaconf.priority(3)


InitializeClass(NewsPublication)


class NewsAddableContents(AddableContents):
    grok.context(INewsPublication)
    REQUIRES = [
        INewsItemContent, INewsItemFilter,
        INewsViewer, INewsPublication, IAsset]


class NewsPublicationCatalogingAttributes(CatalogingAttributes):
    grok.context(INewsPublication)

    @property
    def parent_path(self):
        return '/'.join(self.context.aq_inner.aq_parent.getPhysicalPath())


class NewsPublicationAddForm(silvaforms.SMIAddForm):
    grok.context(INewsPublication)
    grok.name(u"Silva News Publication")


@silvaconf.subscribe(INewsPublication, IContentCreatedEvent)
def news_publication_created(publication, event):
    """news publications should have their 'hide_from_tocs' set to
       'hide'.  This can be done after they are added
    """
    if event.no_default_content:
        return

    binding = getUtility(IMetadataService).getMetadata(publication)
    binding.setValues('silva-settings', {'hide_from_tocs': 'hide'}, reindex=1)
    binding.setValues('snn-np-settings', {'is_private': 'no'}, reindex=1)

    publication.set_silva_addables_allowed_in_container(
        IAddableContents(publication).get_all_addables())

    factory = publication.manage_addProduct['silva.app.news']
    factory.manage_addNewsViewer(
        'index', publication.get_title_or_id())
    factory.manage_addNewsFilter(
        'filter', 'Filter for %s' % publication.get_title_or_id())

    viewer = publication._getOb('index')
    filter = publication._getOb('filter')

    # Configure the new filter and viewer.

    service = getUtility(IServiceNewsCategorization)
    filter.set_subjects(service.get_subjects_tree().get_ids(1))
    filter.set_target_audiences(service.get_target_audiences_tree().get_ids(1))
    filter.add_source(publication)

    viewer.add_filter(filter)


