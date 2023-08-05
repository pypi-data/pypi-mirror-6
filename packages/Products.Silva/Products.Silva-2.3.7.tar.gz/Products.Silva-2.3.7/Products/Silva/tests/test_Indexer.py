# Copyright (c) 2003-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

import unittest

from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva.tests.helpers import publish_object
from Products.Silva.tests import SilvaTestCase

from Products.Silva.Ghost import ghost_factory
from silva.core.interfaces import IIndexer
from silva.core.references.interfaces import IReferenceService


class IndexerTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.pub = self.add_folder(self.root, 'pub', 'Publication')
        self.toghost  = self.add_document(self.root, 'toghost', 'To be Haunted')
        self.gamma  = gamma = self.add_document(self.pub, 'gamma', 'Gamma')
        self.alpha = alpha = self.add_document(self.pub, 'alpha', 'Alpha')
        self.Alpha = Alpha = self.add_document(
            self.pub, 'Alpha', 'Alpha Capital A')
        self.beta = beta = self.add_document(self.pub, 'beta', 'Beta')
        self.Beta = Beta = self.add_document(
            self.pub, 'Beta', 'Beta Capital B')
        self.kappa = kappa = self.add_document(self.pub, 'kappa', 'Kappa')
        self.ghost = ghost = self.add_ghost(self.pub, 'ghost', self.toghost)

        self.foldertoghost = self.add_folder(
            self.root, 'foldertoghost', 'Folder to Ghost')
        self.foo = foo = self.add_document(self.foldertoghost, 'index', 'Index')
        self.bar = bar = self.add_document(self.foldertoghost, 'bar', 'Barrr')
        self.baz = baz = self.add_document(self.foldertoghost, 'baz', 'Bazzz')
        self.ghostfolder = ghost_factory(
            self.pub, 'ghostfolder', self.foldertoghost)
        self.ghostfolder.haunt()
        self.broken_ghost = self.add_ghost(self.root, 'brokenghost', None)

        # add a folder with an indexable index document
        self.subfolder = self.add_folder(
            self.pub, 'folder_with_index_doc',
            'Folder with indexable index document',
            policy_name='Silva Document')

        # also add a folder with a not indexable index document
        self.subfolder_autotoc = self.add_folder(
            self.subfolder, 'folder_with_autotoc',
            'Folder with AutoTOC index document',
            policy_name='Silva AutoTOC')

        getattr(self.subfolder.index, '0').content.manage_edit(
            '<doc>'
            '<p><index name="subfolder" title="subfolder" /></p>'
            '</doc>')
        getattr(self.toghost, '0').content.manage_edit(
            '<doc>'
            '<p><index name="ghost" title="ghost" /></p>'
            '</doc>')
        getattr(gamma, '0').content.manage_edit(
            '<doc>'
            '<p>Foo bar <index name="a" title="a" /></p>'
            '<p>Baz <index name="b" /></p>'
            '</doc>')
        getattr(alpha, '0').content.manage_edit(
            '<doc>'
            '<p>Hey <index name="a" title="a" /></p>'
            '</doc>')
        getattr(Alpha, '0').content.manage_edit(
            '<doc>'
            '<p>Hey <index name="A" title="A" /></p>'
            '</doc>')
        getattr(beta, '0').content.manage_edit(
            '<doc>'
            '<p>Hello <index name="b" title="b" /></p>'
            '</doc>')
        getattr(Beta, '0').content.manage_edit(
            '<doc>'
            '<p>Hello <index name="b" title="b" /></p>'
            '</doc>')
        getattr(kappa, '0').content.manage_edit(
            '<doc>'
            '<p>Dag <index name="c" title="c" /></p>'
            '</doc>')
        getattr(foo, '0').content.manage_edit(
            '<doc>'
            '<p>Dag <index name="f" title="f" /></p>'
            '</doc>')
        getattr(bar, '0').content.manage_edit(
            '<doc>'
            '<p>Dag <index name="g" title="g" /></p>'
            '</doc>')
        getattr(baz, '0').content.manage_edit(
            '<doc>'
            '<p>Dag <index name="h" /></p>'
            '</doc>')

        # publish documents
        for doc in [gamma, alpha, Alpha, beta, Beta, kappa, self.toghost, ghost,
                    self.broken_ghost, self.subfolder.index, foo, bar, baz]:
            publish_object(doc)

        # create one unpublished document that should never show up in the
        # index
        self.omega = self.add_document(self.root, 'omega', 'Omega')

        # create a new version of a document that should not be picked up by the
        # indexer
        gamma.create_copy()
        getattr(gamma, '1').content.manage_edit(
            '<doc>'
            '<p>hello hello <index name="d" /></p>'
            '</doc>')

        # close a version of a document - should also not be picked up by the
        # indexer
        self.Beta.close_version()

        # now create the indexer itself
        self.root.pub.manage_addProduct['Silva'].manage_addIndexer(
            'indexer', 'Title')
        self.indexer = self.pub.indexer
        self.indexer.update()
        self.reference_service = getUtility(IReferenceService)
        def resolver(obj):
            return list(self.reference_service.get_references_between(
                self.indexer, obj, name="indexer"))[0].__name__

        self.resolver = resolver

    def test_indexer(self):
        verifyObject(IIndexer, self.indexer)

    def test_getIndexNames(self):
        self.assertEquals(
            ['A', 'a', 'b', 'c', 'f', 'g', 'ghost', 'subfolder'],
            self.indexer.getIndexNames())

    def test_getIndexEntry(self):
        expected = [
            (u'Alpha', self.resolver(self.alpha), u'a'),
            (u'Gamma', self.resolver(self.gamma), u'a')]
        self.assertEquals(expected, self.indexer.getIndexEntry('a'))

    def test_getAllIndexEntries(self):
        expected = {}
        expected['a'] = [('Alpha', self.resolver(self.alpha), u'a'),
                        ('Gamma', self.resolver(self.gamma), u'a')]
        expected['A'] = [(u'Alpha Capital A', self.resolver(self.Alpha), u'A')]
        expected['b'] = [(u'Beta', self.resolver(self.beta), u'b')]
        expected['c'] = [(u'Kappa', self.resolver(self.kappa), u'c')]
        expected['f'] = [(u'Folder to Ghost', self.resolver(self.ghostfolder), u'f')]
        expected['g'] = [(u'Barrr', self.resolver(self.ghostfolder.bar), u'g')]

        expected['ghost'] = [(u'To be Haunted', self.resolver(self.ghost), u'ghost')]


        expected['subfolder'] = [(u'Folder with indexable index document',
                                 self.resolver(self.subfolder), u'subfolder')]

        result =  self.indexer.getIndexNames()
        self.assertEquals(len(expected), len(result))
        for indexName in result:
            self.assertEquals(expected[indexName],
                              self.indexer.getIndexEntry(indexName))

    def test_remove_entry_when_remove_object(self):
        self.assertEquals([('Alpha', self.resolver(self.alpha), u'a'),
                           ('Gamma', self.resolver(self.gamma), u'a')],
                          self.indexer.getIndexEntry('a'))

        self.pub.manage_delObjects(['alpha'])

        self.assertEquals([('Gamma', self.resolver(self.gamma), u'a')],
                          self.indexer.getIndexEntry('a'))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IndexerTestCase, 'test'))
    return suite
