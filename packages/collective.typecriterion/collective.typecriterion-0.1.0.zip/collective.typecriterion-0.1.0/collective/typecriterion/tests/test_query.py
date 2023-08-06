# -*- coding: utf-8 -*-

import unittest
from collective.typecriterion.interfaces import ITypeCriterionLayer
from collective.typecriterion.interfaces import ITypesCriterionSettings
from collective.typecriterion.persistent import RowTypesCriterionSettings
from collective.typecriterion.testing import TYPE_CRITERION_INTEGRATION_TESTING
from plone.app.querystring.querybuilder import QueryBuilder
from plone.registry.interfaces import IRegistry
from zope import interface
from zope.component import getMultiAdapter
from zope.component import queryUtility


class TestQuery(unittest.TestCase):

    layer = TYPE_CRITERION_INTEGRATION_TESTING

    def setUp(self):
        super(TestQuery, self).setUp()
        registry = queryUtility(IRegistry)
        self.registry = registry.forInterface(ITypesCriterionSettings, check=False)
        portal = self.layer['portal']
        portal.invokeFactory(type_name='Document', id='doc1', title="Document 1")
        portal.invokeFactory(type_name='Document', id='doc2', title="Document 2", subject=['foo'])
        portal.invokeFactory(type_name='News Item', id='news1', title="News 1")
        portal.invokeFactory(type_name='Event', id='event1', title="Event 1", subject=['foo'])

    def test_index_all(self):
        record = RowTypesCriterionSettings(type_name=u'All textual contents',
                                           types_matched=('Document', 'News Item', 'Event'))
        self.registry.type_criterion_defined += (record,)
        portal = self.layer['portal']
        request = self.layer['request']
        qb = QueryBuilder(portal, request)
        query = [{'i': 'general_type', 'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['All textual contents']}]
        results = qb(query)
        self.assertEqual(len(results), 4)
        self.assertTrue('Document 1' in [x.Title() for x in results])
        self.assertTrue('Document 2' in [x.Title() for x in results])
        self.assertTrue('News 1' in [x.Title() for x in results])
        self.assertTrue('Event 1' in [x.Title() for x in results])

    def test_index_none(self):
        record = RowTypesCriterionSettings(type_name=u'Foo',
                                           types_matched=('Document', 'News Item', 'Event'))
        self.registry.type_criterion_defined += (record,)
        portal = self.layer['portal']
        request = self.layer['request']
        qb = QueryBuilder(portal, request)
        query = [{'i': 'general_type', 'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['All textual contents']}]
        results = qb(query)
        self.assertEqual(len(results), 0)

    def test_with_other_criterion(self):
        record = RowTypesCriterionSettings(type_name=u'All textual contents',
                                           types_matched=('Document', 'News Item', 'Event'))
        self.registry.type_criterion_defined += (record,)
        portal = self.layer['portal']
        request = self.layer['request']
        qb = QueryBuilder(portal, request)
        query = [{'i': 'general_type', 'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['All textual contents']},
                 {'i': 'Subject', 'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['foo']}]
        results = qb(query)
        self.assertEqual(len(results), 2)
        self.assertTrue('Document 2' in [x.Title() for x in results])
        self.assertTrue('Event 1' in [x.Title() for x in results])

