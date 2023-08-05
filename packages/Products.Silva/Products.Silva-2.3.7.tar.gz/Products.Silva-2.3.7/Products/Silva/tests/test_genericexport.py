# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

"""Test the generic export feature.
"""

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id$"

# Zope 3
from zope.interface import implements
from zope.interface.verify import verifyObject
from zope.component import getGlobalSiteManager, getUtility
from zope.component.interfaces import ComponentLookupError
from zope.schema.interfaces import IVocabulary

# Silva
from silva.core import interfaces
from Products.Silva.utility import interfaces as interfaces_utility
from Products.SilvaDocument import interfaces as interfaces_document

import SilvaTestCase

class DummyExporter(object):

    implements(interfaces.IContentExporter)

    name = 'Dummy Exporter'
    extension = 'dummy'

    def __init__(self, context):
        self.context = context

    def export(self, settings):
        pass


class ExportTestCase(SilvaTestCase.SilvaTestCase):
    """Test the genereic export feature.
    """

    def afterSetUp(self):
        """Setup some default content.
        """
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva Document')
        testdocument = self.add_document(
            self.root,
            'testdocument',
            'something inside')

    def test_listExport(self):

        # You can list available exporter
        voc = self.root.export_content_format()
        self.failUnless(verifyObject(IVocabulary, voc),
                        "List exporter doesn't return a vocabulary")
        self.assertEqual([(u'zip', 'Full Media (zip)'), 
                          (u'odt', 'Open Document (odt)')],
                         [(v.value, v.title) for v in voc])

        # You can list them against a ref
        ref = self.root.create_ref(self.root.testdocument)
        voc = self.root.export_content_format(ref)
        self.assertEqual([(u'zip', 'Full Media (zip)'), 
                          (u'odt', 'Open Document (odt)')],
                         [(v.value, v.title) for v in voc])

        # We can register exporter for specific content
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(DummyExporter,
                            (interfaces_document.IDocument,),
                            interfaces.IContentExporter,
                            'dummy')

        # Folder will stay unchanged
        voc = self.root.export_content_format()
        self.assertEqual([(u'zip', 'Full Media (zip)'), 
                          (u'odt', 'Open Document (odt)')],
                         [(v.value, v.title) for v in voc])

        # But the exporter is available on document
        voc = self.root.testdocument.export_content_format()
        self.assertEqual([(u'zip', 'Full Media (zip)'),
                          (u'dummy', 'Dummy Exporter'),
                          (u'odt', 'Open Document (odt)'),],
                         [(v.value, v.title) for v in voc],)

        # Remove our test exporter
        gsm.unregisterAdapter(DummyExporter,
                              (interfaces_document.IDocument,),
                              interfaces.IContentExporter,
                              'dummy')

        
    def test_exportUtility(self):

        # There is an utility which manage export feature
        utility = getUtility(interfaces_utility.IExportUtility)
        self.failUnless(verifyObject(interfaces_utility.IExportUtility, 
                                     utility),)

        # We have a function to list exporter (see test_listExport),
        # which return a vocabulary
        voc = utility.listContentExporter(self.root)
        self.assertEqual([(u'zip', 'Full Media (zip)'), 
                          (u'odt', 'Open Document (odt)'),],
                         [(v.value, v.title) for v in voc],)

        # Add we can retrieve the default zip exporter
        zip_exporter = utility.createContentExporter(self.root, 'zip')
        self.failUnless(verifyObject(interfaces.IContentExporter,
                                     zip_exporter),)

        # A non-existant exporter give a lookup error error
        self.assertRaises(ComponentLookupError, 
                          utility.createContentExporter, self.root, 'invalid')



import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExportTestCase))
    return suite    
