# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import Interface

from Products.Silva.transform.interfaces import IRenderable


class RenderableAdapter(grok.Adapter):
    grok.context(Interface)     # XXX Should be ISilvaObject or IVersion
    grok.provides(IRenderable)
    grok.implements(IRenderable)

    def view(self, request=None):
        """Display the view of this version using the selected renderer.

        Returns the rendered content or None if no renderer can be
        found.
        """
        renderer_name = self.context.get_renderer_name()
        renderer = self.context.service_renderer_registry.getRenderer(
            self.context.get_silva_object().meta_type, renderer_name)
        if renderer is None:
            return None
        return renderer.transform(self.context, request)


