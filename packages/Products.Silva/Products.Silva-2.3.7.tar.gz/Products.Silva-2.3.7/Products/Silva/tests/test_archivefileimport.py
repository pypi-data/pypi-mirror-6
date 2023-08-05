# Copyright (c) 2003-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject

from Products.Silva.tests.helpers import open_test_file
from Products.Silva.testing import FunctionalLayer, TestCase

from AccessControl import getSecurityManager
from Products.Silva.adapters.archivefileimport import (
    getArchiveFileImportAdapter)
from silva.core import interfaces


"""
Test file 'test1.zip' structure:

  testzip
  |-- Clock.swf
  |-- bar
  |   `-- image2.jpg
  |-- foo
  |   |-- bar
  |   |   |-- baz
  |   |   |   `-- image5.jpg
  |   |   `-- image4.jpg
  |   `-- image3.jpg
  |-- image1.jpg
  `-- sound1.mp3

Test file 'test2.zip' structure:

  Clock.swf
  image1.jpg
  sound1.mp3

Test file 'test3.zip' structure:

  imgs
  |--c16.png
  |--c17.png
  |--.DS_Store

  __MACOSX
  |--[various files]
"""


class ArchiveFileImportTestCase(TestCase):
    """Test the archive file importer.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addLink(
            'link', 'Link', relative=False, url="http:/infrae.com")

    def test_adapter(self):
        """Test adapter lookup.
        """
        importer = interfaces.IArchiveFileImporter(self.root.folder, None)
        self.failUnless(
            verifyObject(interfaces.IArchiveFileImporter, importer))
        self.failUnless(
            interfaces.IArchiveFileImporter(self.root.link, None) is None)

    def test_smi_adapter(self):
        """Test adapter  query for SMI / SMI right access
        """
        importer = getArchiveFileImportAdapter(self.root.folder)
        self.failUnless(
            verifyObject(interfaces.IArchiveFileImporter, importer))
        security = getSecurityManager()
        self.failUnless(
            security.checkPermission(
                'Change Silva content', importer))

    def test_import_default_settings(self):
        """Import a Zip file.
        """
        folder = self.root.folder
        importer = interfaces.IArchiveFileImporter(folder)
        succeeded, failed = importer.importArchive(open_test_file('test1.zip'))

        self.assertListEqual(succeeded,
                             ['testzip/foo/bar/baz/image5.jpg',
                              'testzip/foo/bar/image4.jpg',
                              'testzip/foo/image3.jpg',
                              'testzip/bar/image2.jpg',
                              'testzip/image1.jpg',
                              'testzip/sound1.mp3',
                              'testzip/Clock.swf'])
        self.assertListEqual([], failed)

        self.assert_(folder['testzip'])
        self.assert_(folder['testzip']['bar'])
        self.assert_(folder['testzip']['foo'])
        self.assert_(folder['testzip']['foo']['bar'])
        self.assert_(folder['testzip']['foo']['bar']['baz'])

        self.failUnless(interfaces.IImage.providedBy(
                folder['testzip']['image1.jpg']))
        self.failUnless(interfaces.IFile.providedBy(
                folder['testzip']['sound1.mp3']))
        self.failUnless(interfaces.IFile.providedBy(
                folder['testzip']['Clock.swf']))
        self.failUnless(interfaces.IImage.providedBy(
                folder['testzip']['bar']['image2.jpg']))
        self.failUnless(interfaces.IImage.providedBy(
                folder['testzip']['foo']['bar']['baz']['image5.jpg']))

    def test_import_no_sub_dirs(self):
        """Import a Zip that doesn't have any subdirectories.
        """
        folder = self.root.folder
        importer = interfaces.IArchiveFileImporter(folder)
        succeeded, failed = importer.importArchive(open_test_file('test2.zip'))

        self.assertListEqual(
            succeeded, ['Clock.swf', 'image1.jpg', 'sound1.mp3'])
        self.assertListEqual(failed, [])

        self.assertListEqual(
            succeeded, ['Clock.swf', 'image1.jpg', 'sound1.mp3'])
        self.assertListEqual([], failed)
        self.assertListEqual(
            folder.objectIds(), ['Clock.swf', 'image1.jpg', 'sound1.mp3'])
        self.failUnless(interfaces.IImage.providedBy(folder['image1.jpg']))
        self.failUnless(interfaces.IFile.providedBy(folder['sound1.mp3']))
        self.failUnless(interfaces.IFile.providedBy(folder['Clock.swf']))

    def test_import_asset_set_title(self):
        """Set a default title to the imported assets.
        """
        folder = self.root.folder
        importer = interfaces.IArchiveFileImporter(folder)
        succeeded, failed = importer.importArchive(
            open_test_file('test1.zip'), assettitle=u'Daarhelemali')

        self.assertListEqual(failed, [])
        self.assertEquals(
            u'Daarhelemali',
            folder['testzip']['bar']['image2.jpg'].get_title())
        self.assertEquals(
            u'Daarhelemali',
            folder['testzip']['foo']['bar']['baz']['image5.jpg'].get_title())

    def test_import_no_recreate_directory(self):
        """Import a ZIP which have subdirectories with the setting don't
        create directories.
        """
        folder = self.root.folder
        importer = interfaces.IArchiveFileImporter(folder)
        succeeded, failed = importer.importArchive(
            open_test_file('test1.zip'), recreatedirs=0)

        self.assertListEqual(
            succeeded,
            ['testzip/foo/bar/baz/image5.jpg', 'testzip/foo/bar/image4.jpg',
             'testzip/foo/image3.jpg', 'testzip/bar/image2.jpg',
             'testzip/image1.jpg', 'testzip/sound1.mp3', 'testzip/Clock.swf'])
        self.assertListEqual(failed, [])
        self.assertListEqual(
            folder.objectIds(),
            ['testzip_Clock.swf', 'testzip_bar_image2.jpg',
             'testzip_foo_bar_baz_image5.jpg', 'testzip_foo_bar_image4.jpg',
             'testzip_foo_image3.jpg', 'testzip_image1.jpg',
             'testzip_sound1.mp3'])

        self.failUnless(interfaces.IImage.providedBy(
                folder['testzip_image1.jpg']))
        self.failUnless(interfaces.IFile.providedBy(
                folder['testzip_sound1.mp3']))
        self.failUnless(interfaces.IFile.providedBy(
                folder['testzip_Clock.swf']))

    def test_import_no_recreate_directory2(self):
        """Import a ZIP without directories with the setting don't
        create directories.
        """
        folder = self.root.folder
        importer = interfaces.IArchiveFileImporter(folder)
        succeeded, failed = importer.importArchive(
            open_test_file('test2.zip'), recreatedirs=0)

        self.assertListEqual(
            succeeded, ['Clock.swf', 'image1.jpg', 'sound1.mp3'])
        self.assertListEqual([], failed)
        self.assertListEqual(
            folder.objectIds(), ['Clock.swf', 'image1.jpg', 'sound1.mp3'])
        self.failUnless(interfaces.IImage.providedBy(folder['image1.jpg']))
        self.failUnless(interfaces.IFile.providedBy(folder['sound1.mp3']))
        self.failUnless(interfaces.IFile.providedBy(folder['Clock.swf']))

    def test_import_macos_files(self):
        """Import an archive file that have Macos X metadata
        directories. They should be ignored.
        """
        folder = self.root.folder
        importer = interfaces.IArchiveFileImporter(folder)
        succeeded, failed = importer.importArchive(open_test_file('test3.zip'))

        self.assertListEqual(succeeded, ['imgs/c16.png', 'imgs/c17.png'])
        self.assertListEqual([], failed)

        self.assertListEqual(folder.objectIds(), ['imgs'])
        self.assertListEqual(folder.imgs.objectIds(), ['c16.png', 'c17.png'])

        self.failUnless(interfaces.IImage.providedBy(
                folder['imgs']['c16.png']))
        self.failUnless(interfaces.IImage.providedBy(
                folder['imgs']['c17.png']))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ArchiveFileImportTestCase))
    return suite
