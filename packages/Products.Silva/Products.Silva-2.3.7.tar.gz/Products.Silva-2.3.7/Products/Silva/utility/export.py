# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from zope.component import getAdapter, getAdapters
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from silva.core.interfaces.adapters import IContentExporter, \
    IDefaultContentExporter
from Products.Silva.utility.interfaces import IExportUtility


class ExportUtility(grok.GlobalUtility):
    """Utility to manage export.
    """

    grok.implements(IExportUtility)

    def createContentExporter(self, context, name):
        """Create a content exporter.
        """
        return getAdapter(context, IContentExporter, name=name)

    def listContentExporter(self, context):
        """List available exporter.
        """

        default = None
        all = []
        for adapter in getAdapters((context,), IContentExporter):
            term = SimpleTerm(value=adapter[0], title=adapter[1].name)
            if IDefaultContentExporter.providedBy(adapter[1]):
                if not default:
                    default = term
                else:
                    assert "There is two default content exporter"
            else:
                all.append(term)
        return SimpleVocabulary([default,] + all)

