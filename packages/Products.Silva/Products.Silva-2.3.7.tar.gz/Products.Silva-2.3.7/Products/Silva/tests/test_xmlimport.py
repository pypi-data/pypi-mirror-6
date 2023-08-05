# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from StringIO import StringIO
from zipfile import ZipFile
import unittest

from DateTime import DateTime
from Acquisition import aq_chain

from zope.component import getUtility
from zope.component.eventtesting import clearEvents
from silva.core import interfaces
from silva.core.interfaces.events import IContentImported

from Products.Silva.silvaxml import xmlimport
from Products.Silva.testing import FunctionalLayer
from Products.Silva.testing import TestCase
from Products.Silva.tests.helpers import open_test_file
from Products.SilvaMetadata.interfaces import IMetadataService


class SilvaXMLTestCase(TestCase):
    """Test case with some helpers to work with XML import.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        self.metadata = getUtility(IMetadataService)
        # setUp triggered some events. Clear them.
        clearEvents()

    def import_file(self, filename, globs=None, replace=False):
        """Import an XML file.
        """
        if globs is None:
            globs = globals()
        with open_test_file(filename, globs) as source_file:
            xmlimport.importFromFile(
                source_file, self.root, replace=replace)

    def import_zip(self, filename, globs=None, replace=False):
        """Import a ZIP file.
        """
        if globs is None:
            globs = globals()
        with open_test_file(filename, globs) as source_file:
            source_zip = ZipFile(source_file)
            info = xmlimport.ImportInfo()
            info.setZIPFile(source_zip)
            import_file = StringIO(source_zip.read('silva.xml'))
            xmlimport.importFromFile(
                import_file, self.root, info=info, replace=replace)


class XMLImportTestCase(SilvaXMLTestCase):
    """Import data from an XML file.
    """

    def test_publication(self):
        """Test import of publication.
        """
        self.import_file('test_import_publication.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/publication',
             'ContentImported for /root/publication/index'],
            IContentImported)

        publication = self.root.publication
        binding = self.metadata.getMetadata(publication)

        self.assertTrue(interfaces.IPublication.providedBy(publication))
        self.assertEqual(publication.get_title(), u'Test Publication')
        self.assertEqual(binding.get('silva-extra', 'creator'), u'admin')
        self.assertEqual(
            binding.get('silva-content', 'maintitle'), u'Test Publication')

    def test_folder(self):
        """Test folder import.
        """
        self.import_file('test_import_folder.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/subfolder'],
            IContentImported)
        self.assertListEqual(self.root.folder.objectIds(), ['subfolder'])

        folder = self.root.folder
        binding = self.metadata.getMetadata(folder)

        self.assertTrue(interfaces.IFolder.providedBy(folder))
        self.assertEqual(folder.get_title(), u'Test Folder')
        self.assertEqual(binding.get('silva-extra', 'creator'), u'admin')
        self.assertEqual(binding.get('silva-extra', 'lastauthor'), u'admin')
        self.assertEqual(
            binding.get('silva-extra', 'contactname'), u'Henri McArthur')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'This folder have been created only in testing purpose.')
        self.assertEqual(
            binding.get('silva-content', 'maintitle'), u'Test Folder')

        subfolder = folder.subfolder
        binding = self.metadata.getMetadata(subfolder)

        self.assertEqual(subfolder.get_title(), u'Second test folder')
        self.assertEqual(binding.get('silva-extra', 'creator'), u'henri')
        self.assertEqual(binding.get('silva-extra', 'lastauthor'), u'henri')

    def test_link_to_file(self):
        """Import a link that is linked to a file.
        """
        self.import_zip('test_import_link.zip')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/file',
             'ContentImported for /root/folder/index',
             'ContentImported for /root/folder/new',
             'ContentImported for /root/folder/new/link'],
            IContentImported)
        self.assertListEqual(
            self.root.folder.objectIds(),
            ['file', 'index', 'new'])
        self.assertListEqual(
            self.root.folder.new.objectIds(),
            ['link'])

        link = self.root.folder.new.link
        datafile = self.root.folder.file

        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))
        self.assertEqual(datafile.get_title(),  u'Torvald file')

        version = link.get_editable()
        self.assertFalse(version is None)
        self.assertEqual(link.get_viewable(), None)
        self.assertEqual(version.get_title(), u'Last file')
        self.assertEqual(
            DateTime('2004-04-23T16:13:39Z'),
            version.get_modification_datetime())

        binding = self.metadata.getMetadata(version)
        self.assertEqual(binding.get('silva-extra', 'creator'), u'henri')
        self.assertEqual(binding.get('silva-extra', 'lastauthor'), u'henri')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'Link to the lastest file.')

        self.assertEqual(version.get_relative(), True)
        self.assertEqual(version.get_target(), datafile)
        self.assertEqual(aq_chain(version.get_target()), aq_chain(datafile))

        binding = self.metadata.getMetadata(datafile)
        self.assertEqual(binding.get('silva-extra', 'creator'), u'pauline')
        self.assertEqual(binding.get('silva-extra', 'lastauthor'), u'pauline')
        self.assertEqual(
            binding.get('silva-extra', 'comment'),
            u'This file contains Torvald lastest whereabouts.')

    def test_link_to_file_existing_replace(self):
        """Import a link to file in a folder that already exists. It
        replace the ids, it doesn't check if the types are the same.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        self.import_zip('test_import_link.zip', replace=True)
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/file',
             'ContentImported for /root/folder/index',
             'ContentImported for /root/folder/new',
             'ContentImported for /root/folder/new/link'],
            IContentImported)
        self.assertTrue(interfaces.IFolder.providedBy(self.root.folder))
        self.assertListEqual(
            self.root.folder.objectIds(),
            ['file', 'index', 'new'])
        self.assertListEqual(
            self.root.folder.new.objectIds(),
            ['link'])

        link = self.root.folder.new.link
        datafile = self.root.folder.file

        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))
        self.assertEqual(datafile.get_title(),  u'Torvald file')

        version = link.get_editable()
        self.assertEqual(version.get_relative(), True)
        self.assertEqual(version.get_target(), datafile)
        self.assertEqual(aq_chain(version.get_target()), aq_chain(datafile))

    def test_link_to_file_existing_rename(self):
        """Import a link to file in a folder that already exists. The
        imported folder should be done under a different name.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        indexer = self.root.folder
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        self.import_zip('test_import_link.zip')
        self.assertEventsAre(
            ['ContentImported for /root/import_of_folder',
             'ContentImported for /root/import_of_folder/file',
             'ContentImported for /root/import_of_folder/index',
             'ContentImported for /root/import_of_folder/new',
             'ContentImported for /root/import_of_folder/new/link'],
            IContentImported)
        self.assertTrue(
            interfaces.IFolder.providedBy(self.root.import_of_folder))
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))
        self.assertEqual(indexer, self.root.folder)
        self.assertListEqual(
            self.root.import_of_folder.objectIds(),
            ['file', 'index', 'new'])
        self.assertListEqual(
            self.root.import_of_folder.new.objectIds(),
            ['link'])

        link = self.root.import_of_folder.new.link
        datafile = self.root.import_of_folder.file

        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))
        self.assertEqual(datafile.get_title(),  u'Torvald file')

        version = link.get_editable()
        self.assertEqual(version.get_relative(), True)
        self.assertEqual(version.get_target(), datafile)
        self.assertEqual(aq_chain(version.get_target()), aq_chain(datafile))

    def test_link_to_file_existing_rename_twice(self):
        """Import a link to file in a folder that already exists two times. The
        imported folder should be done under a different name for each import.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        self.import_zip('test_import_link.zip')
        self.assertEventsAre(
            ['ContentImported for /root/import_of_folder',
             'ContentImported for /root/import_of_folder/file',
             'ContentImported for /root/import_of_folder/index',
             'ContentImported for /root/import_of_folder/new',
             'ContentImported for /root/import_of_folder/new/link'],
            IContentImported)
        self.assertTrue(
            interfaces.IFolder.providedBy(self.root.import_of_folder))
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        clearEvents()

        self.import_zip('test_import_link.zip')
        self.assertEventsAre(
            ['ContentImported for /root/import2_of_folder',
             'ContentImported for /root/import2_of_folder/file',
             'ContentImported for /root/import2_of_folder/index',
             'ContentImported for /root/import2_of_folder/new',
             'ContentImported for /root/import2_of_folder/new/link'],
            IContentImported)
        self.assertTrue(
            interfaces.IFolder.providedBy(self.root.import2_of_folder))
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        link = self.root.import_of_folder.new.link
        datafile = self.root.import_of_folder.file

        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))
        self.assertEqual(datafile.get_title(),  u'Torvald file')

        version = link.get_editable()
        self.assertEqual(version.get_relative(), True)
        self.assertEqual(version.get_target(), datafile)
        self.assertEqual(aq_chain(version.get_target()), aq_chain(datafile))

        link2 = self.root.import2_of_folder.new.link
        datafile2 = self.root.import2_of_folder.file

        self.assertTrue(interfaces.ILink.providedBy(link2))
        self.assertTrue(interfaces.IFile.providedBy(datafile2))
        self.assertEqual(datafile2.get_title(),  u'Torvald file')

        version2 = link2.get_editable()
        self.assertEqual(version2.get_relative(), True)
        self.assertEqual(version2.get_target(), datafile2)
        self.assertEqual(aq_chain(version2.get_target()), aq_chain(datafile2))

    def test_link_url(self):
        """Import a link set with an URL.
        """
        self.import_file('test_import_link.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/index',
             'ContentImported for /root/folder/link'],
            IContentImported)
        self.assertListEqual(
            self.root.folder.objectIds(),
            ['index', 'link'])

        link = self.root.folder.link

        version = link.get_viewable()
        self.assertFalse(version is None)
        self.assertEqual(link.get_editable(), None)
        self.assertEqual(version.get_title(), u'Best website')

        binding = self.metadata.getMetadata(version)
        self.assertEqual(binding.get('silva-extra', 'creator'), u'wimbou')
        self.assertEqual(binding.get('silva-extra', 'lastauthor'), u'wimbou')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'Best website in the world.')

        self.assertEqual(version.get_relative(), False)
        self.assertEqual(version.get_url(), 'http://wimbou.be')

    def test_broken_metadata(self):
        """Import a file that refer to unknown metadata set and
        elements.
        """
        self.import_file('test_import_metadata.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/publication'],
            IContentImported)

        publication = self.root.publication
        self.assertTrue(interfaces.IPublication.providedBy(publication))

    def test_broken_references(self):
        """Import a file with broken references.
        """
        self.import_file('test_import_broken_references.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/ghost',
             'ContentImported for /root/folder/link'],
            IContentImported)

        ghost_version = self.root.folder.ghost.get_editable()
        self.assertNotEqual(ghost_version, None)
        self.assertEqual(ghost_version.get_haunted(), None)
        self.assertEqual(ghost_version.get_link_status(), ghost_version.LINK_EMPTY)

        link_version = self.root.folder.link.get_editable()
        self.assertNotEqual(link_version, None)
        self.assertEqual(link_version.get_relative(), True)
        self.assertEqual(link_version.get_target(), None)

    def test_fallback(self):
        """Import an archive that contain a ZEXP.
        """
        self.import_zip('test_import_fallback.zip')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/zope2folder'],
            IContentImported)
        folder = self.root.folder
        self.assertEqual(folder.get_title(), u"Stuff's container")
        self.assertEqual(folder.objectIds(), ['zope2folder'])
        self.assertEqual(folder.zope2folder.meta_type, 'Folder')

    def test_fallback_existing(self):
        """Import an archive that contain a ZEXP with an object that
        already exists.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Existing folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('zope2folder', 'Existing Zope 2 Stuff')
        factory.manage_addIndexer('indexer', 'Index Zope 2 Stuff')

        self.import_zip('test_import_fallback.zip')
        self.assertEventsAre(
            ['ContentImported for /root/import_of_folder',
             'ContentImported for /root/import_of_folder/zope2folder'],
            IContentImported)

        folder = self.root.import_of_folder
        self.assertEqual(folder.get_title(), u"Stuff's container")
        self.assertEqual(folder.objectIds(), ['zope2folder'])
        self.assertEqual(folder.zope2folder.meta_type, 'Folder')

    def test_fallback_existing_replace(self):
        """Import an archive that contain a ZEXP with an object that
        already exists.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Existing folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('zope2folder', 'Existing Zope 2 Stuff')
        factory.manage_addIndexer('indexer', 'Index Zope 2 Stuff')

        self.import_zip('test_import_fallback.zip', replace=True)
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/zope2folder'],
            IContentImported)

        folder = self.root.folder
        self.assertEqual(folder.get_title(), u"Stuff's container")
        self.assertEqual(folder.objectIds(), ['zope2folder'])
        self.assertEqual(folder.zope2folder.meta_type, 'Folder')

    def test_ghost_to_image(self):
        """Import a ghost to an image.
        """
        self.import_zip('test_import_ghost.zip')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/images',
             'ContentImported for /root/folder/images/ghost_of_torvald_jpg',
             'ContentImported for /root/folder/torvald_jpg'],
            IContentImported)
        self.assertListEqual(
            self.root.folder.objectIds(),
            ['images', 'torvald_jpg'])
        self.assertListEqual(
            self.root.folder.images.objectIds(),
            ['ghost_of_torvald_jpg'])

        image = self.root.folder.torvald_jpg
        ghost = self.root.folder.images.ghost_of_torvald_jpg
        self.assertTrue(interfaces.IImage.providedBy(image))
        self.assertTrue(interfaces.IGhost.providedBy(ghost))

        version = ghost.get_viewable()
        self.assertFalse(version is None)
        self.assertEqual(ghost.get_editable(), None)
        self.assertEqual(version.get_title(), u'Torvald picture')
        self.assertEqual(image.get_title(), u'Torvald picture')
        self.assertEqual(version.get_haunted(), image)
        self.assertEqual(aq_chain(version.get_haunted()), aq_chain(image))

        binding = self.metadata.getMetadata(image)
        self.assertEqual(binding.get('silva-extra', 'creator'), u'pauline')
        self.assertEqual(binding.get('silva-extra', 'lastauthor'), u'pauline')
        self.assertEqual(
            binding.get('silva-extra', 'comment'),
            u'Torvald public face.')

    def test_ghost_to_image_existing_replace(self):
        """Import a ghost to an image.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        self.import_zip('test_import_ghost.zip', replace=True)
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/images',
             'ContentImported for /root/folder/images/ghost_of_torvald_jpg',
             'ContentImported for /root/folder/torvald_jpg'],
            IContentImported)
        self.assertTrue(interfaces.IFolder.providedBy(self.root.folder))
        self.assertListEqual(
            self.root.folder.objectIds(),
            ['images', 'torvald_jpg'])
        self.assertListEqual(
            self.root.folder.images.objectIds(),
            ['ghost_of_torvald_jpg'])

        image = self.root.folder.torvald_jpg
        ghost = self.root.folder.images.ghost_of_torvald_jpg
        self.assertTrue(interfaces.IImage.providedBy(image))
        self.assertTrue(interfaces.IGhost.providedBy(ghost))

        version = ghost.get_viewable()
        self.assertEqual(version.get_haunted(), image)
        self.assertEqual(aq_chain(version.get_haunted()), aq_chain(image))

    def test_ghost_to_image_existing_rename(self):
        """Import a ghost to an image.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        self.import_zip('test_import_ghost.zip')
        self.assertEventsAre(
            ['ContentImported for /root/import_of_folder',
             'ContentImported for /root/import_of_folder/images',
             'ContentImported for /root/import_of_folder/images/ghost_of_torvald_jpg',
             'ContentImported for /root/import_of_folder/torvald_jpg'],
            IContentImported)
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))
        self.assertTrue(
            interfaces.IFolder.providedBy(self.root.import_of_folder))
        self.assertListEqual(
            self.root.import_of_folder.objectIds(),
            ['images', 'torvald_jpg'])
        self.assertListEqual(
            self.root.import_of_folder.images.objectIds(),
            ['ghost_of_torvald_jpg'])

        image = self.root.import_of_folder.torvald_jpg
        ghost = self.root.import_of_folder.images.ghost_of_torvald_jpg
        self.assertTrue(interfaces.IImage.providedBy(image))
        self.assertTrue(interfaces.IGhost.providedBy(ghost))

        version = ghost.get_viewable()
        self.assertEqual(version.get_haunted(), image)
        self.assertEqual(aq_chain(version.get_haunted()), aq_chain(image))

    def test_indexer(self):
        """Import an indexer.
        """
        self.import_file('test_import_indexer.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/indexer'],
            IContentImported)
        self.assertListEqual(self.root.folder.objectIds(), ['indexer'])

        indexer = self.root.folder.indexer
        self.assertTrue(interfaces.IIndexer.providedBy(indexer))
        self.assertEqual(indexer.get_title(), u'Index of this site')

        binding = self.metadata.getMetadata(indexer)
        self.assertEqual(binding.get('silva-extra', 'creator'), u'antoine')
        self.assertEqual(binding.get('silva-extra', 'lastauthor'), u'antoine')
        self.assertEqual(
            binding.get('silva-extra', 'comment'),
            u'Nothing special is required.')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'Index the content of your website.')

    def test_ghost_folder(self):
        """Import a ghost folder that contains various things.
        """
        self.import_file('test_import_ghostfolder.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/container',
             'ContentImported for /root/folder/container/indexer',
             'ContentImported for /root/folder/container/link',
             'ContentImported for /root/folder/ghost'],
            IContentImported)
        self.assertListEqual(
            self.root.folder.objectIds(), ['container', 'ghost'])
        self.assertListEqual(
            self.root.folder.container.objectIds(), ['indexer', 'link'])

        folder = self.root.folder.ghost
        container = self.root.folder.container
        self.assertTrue(interfaces.IGhostFolder.providedBy(folder))
        self.assertEqual(folder.get_haunted(), container)
        self.assertEqual(aq_chain(folder.get_haunted()), aq_chain(container))
        self.assertListEqual(folder.objectIds(), container.objectIds())

    def test_ghost_folder_existing_rename(self):
        """Import a ghost folder with an ID of a already existing element.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        self.import_file('test_import_ghostfolder.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/import_of_folder',
             'ContentImported for /root/import_of_folder/container',
             'ContentImported for /root/import_of_folder/container/indexer',
             'ContentImported for /root/import_of_folder/container/link',
             'ContentImported for /root/import_of_folder/ghost'],
            IContentImported)
        self.assertFalse(
            interfaces.IFolder.providedBy(self.root.folder))
        self.assertTrue(
            interfaces.IFolder.providedBy(self.root.import_of_folder))
        self.assertListEqual(
            self.root.import_of_folder.objectIds(),
            ['container', 'ghost'])
        self.assertListEqual(
            self.root.import_of_folder.container.objectIds(),
            ['indexer', 'link'])

        folder = self.root.import_of_folder.ghost
        container = self.root.import_of_folder.container
        self.assertTrue(interfaces.IGhostFolder.providedBy(folder))
        self.assertEqual(folder.get_haunted(), container)
        self.assertEqual(aq_chain(folder.get_haunted()), aq_chain(container))
        self.assertListEqual(folder.objectIds(), container.objectIds())

    def test_autotoc(self):
        """Import some autotoc.
        """
        self.import_file('test_import_autotoc.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/assets',
             'ContentImported for /root/folder/index'],
            IContentImported)
        self.assertListEqual(self.root.folder.objectIds(), ['assets', 'index'])

        assets = self.root.folder.assets
        containers = self.root.folder.index
        self.assertTrue(interfaces.IAutoTOC.providedBy(assets))
        self.assertTrue(interfaces.IAutoTOC.providedBy(containers))
        self.assertEqual(assets.get_title(), u'Local assets')
        self.assertEqual(containers.get_title(), u'Containers')

        self.assertEqual(assets.get_show_icon(), True)
        self.assertEqual(containers.get_show_icon(), False)
        self.assertEqual(assets.get_toc_depth(), -1)
        self.assertEqual(containers.get_toc_depth(), 42)
        self.assertListEqual(
            assets.get_local_types(),
            [u'Silva File', u'Silva Image'])
        self.assertListEqual(
            containers.get_local_types(),
            [u'Silva Folder', u'Silva Publication'])

        binding = self.metadata.getMetadata(assets)
        self.assertEqual(
            binding.get('silva-extra', 'creator'), u'hacker-kun')
        self.assertEqual(
            binding.get('silva-extra', 'lastauthor'), u'hacker-kun')
        self.assertEqual(
            binding.get('silva-extra', 'hide_from_tocs'),
            u'do not hide')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'Report local assets.')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLImportTestCase))
    return suite
