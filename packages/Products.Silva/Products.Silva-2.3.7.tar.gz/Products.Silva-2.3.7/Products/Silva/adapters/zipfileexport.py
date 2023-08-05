# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from cStringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED

from five import grok
from silva.core import interfaces
import transaction

from Products.Silva.silvaxml import xmlexport


class ZipFileExportAdapter(grok.Adapter):
    """ Adapter for silva objects to facilitate
    the export to zipfiles.
    """
    grok.implements(interfaces.IDefaultContentExporter)
    grok.provides(interfaces.IContentExporter)
    grok.context(interfaces.ISilvaObject)
    grok.name('zip')

    name = "Full Media (zip)"
    extension = "zip"

    def export(self, settings=None):
        archive_file = StringIO()
        archive = ZipFile(archive_file, "w", ZIP_DEFLATED)

        # export context to xml and add xml to zip
        xml, info = xmlexport.exportToString(self.context, settings)
        archive.writestr('silva.xml', xml)

        # process data from the export, i.e. export binaries
        for path, id in info.getAssetPaths():
            asset = self.context.restrictedTraverse(path)
            adapter = interfaces.IAssetData(asset)
            archive.writestr('assets/' + id, adapter.getData())

        unknowns = info.getZexpPaths()
        if unknowns:
            # This is required is exported content have been created
            # in the same transaction than the export. They need to be
            # in the database in order to be exported.
            transaction.savepoint()
            for path, id in unknowns:
                export = StringIO()
                content = self.context.restrictedTraverse(path)
                content._p_jar.exportFile(content._p_oid, export)
                archive.writestr('zexps/' + id, export.getvalue())
                export.close()

        archive.close()
        return archive_file.getvalue()





