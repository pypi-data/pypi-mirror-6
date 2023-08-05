# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from zope.component import getUtility, queryAdapter
from zope.interface.verify import verifyObject

from Products.Silva.testing import tests, Transaction
from silva.core.services.interfaces import IMetadataService

from silva.core.interfaces import IAddableContents
from silva.app.news.testing import FunctionalLayer
from silva.app.news.interfaces import INewsPublication
from silva.app.news.interfaces import INewsFilter, INewsViewer


class NewsPublicationTestCase(unittest.TestCase):
    """Test the NewsPublication interface.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_publication(self):
        """Verify a news publication publication and its default
        metadata and contents.
        """
        with Transaction():
            factory = self.root.manage_addProduct['silva.app.news']
            with tests.assertTriggersEvents('ContentCreatedEvent'):
                factory.manage_addNewsPublication('news', 'News')

        publication = self.root._getOb('news', None)
        self.assertTrue(verifyObject(INewsPublication, publication))

        # Default settings
        get_metadata = getUtility(IMetadataService).getMetadataValue
        self.assertEqual(
            get_metadata(publication, 'silva-settings', 'hide_from_tocs'),
            'hide')
        self.assertEqual(
            get_metadata(publication, 'snn-np-settings', 'is_private'),
            'no')

        # Default content
        self.assertNotEqual(publication.get_creation_datetime(), None)
        self.assertNotEqual(publication.get_modification_datetime(), None)
        self.assertItemsEqual(publication.objectIds(), ['index', 'filter'])
        self.assertTrue(verifyObject(INewsViewer, publication.index))
        self.assertTrue(verifyObject(INewsFilter, publication.filter))

    def test_addables(self):
        """Verify that the addable content is restricted inside a news
        publication.
        """
        with Transaction():
            factory = self.root.manage_addProduct['silva.app.news']
            factory.manage_addNewsPublication('news', 'News')

        publication = self.root._getOb('news', None)
        addables = queryAdapter(publication, IAddableContents)
        self.assertTrue(verifyObject(IAddableContents, addables))
        self.assertItemsEqual(
            addables.get_container_addables(),
            ['Silva Image',
             'Silva File',
             'Mockup Asset',
             'Silva Ghost Asset',
             'Silva CSV Source',
             'Silva News Publication',
             'Silva News Viewer',
             'Silva News Filter',
             'Silva Agenda Viewer',
             'Silva Agenda Filter',
             'Silva News Item',
             'Silva Agenda Item',])
        self.assertItemsEqual(
            addables.get_all_addables(),
            ['Silva Image',
             'Silva File',
             'Mockup Asset',
             'Silva Ghost Asset',
             'Silva CSV Source',
             'Silva News Publication',
             'Silva News Viewer',
             'Silva News Filter',
             'Silva Agenda Viewer',
             'Silva Agenda Filter',
             'Silva News Item',
             'Silva Agenda Item'])

        # News Item and Agenda Item are not addables in the root
        root_addables = IAddableContents(self.root).get_container_addables()
        self.assertFalse('Silva News Item' in root_addables)
        self.assertFalse('Silva Agenda Item' in root_addables)

    def test_catalog(self):
        """Verify cataloging.
        """

        def search(query):
            return map(lambda b: (b.getPath(), b.publication_status),
                       self.root.service_catalog(**query))

        self.assertItemsEqual(
            search({'meta_type': 'Silva News Publication',
                    'snn-np-settingsis_private': 'yes'}),
            [])
        self.assertItemsEqual(
            search({'meta_type': 'Silva News Publication',
                    'snn-np-settingsis_private': 'no'}),
            [])

        with Transaction(catalog=True):
            factory = self.root.manage_addProduct['silva.app.news']
            factory.manage_addNewsPublication('news', 'News')

        self.assertItemsEqual(
            search({'meta_type': 'Silva News Publication',
                    'snn-np-settingsis_private': 'yes'}),
            [])
        self.assertItemsEqual(
            search({'meta_type': 'Silva News Publication',
                    'snn-np-settingsis_private': 'no'}),
            [('/root/news', 'public')])



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsPublicationTestCase))
    return suite
