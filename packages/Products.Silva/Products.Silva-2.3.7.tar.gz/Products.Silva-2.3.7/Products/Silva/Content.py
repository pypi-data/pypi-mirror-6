# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import warnings

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass # Zope 2.12

# Silva
from Products.Silva.Publishable import Publishable
from Products.Silva import SilvaPermissions

from silva.core.interfaces import IContent
from silva.core import conf as silvaconf
from zope.interface import implements


class Content(Publishable):

    silvaconf.baseclass()
    security = ClassSecurityInfo()
    implements(IContent)

    object_type = 'content'

    # use __init__ of SilvaObject

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                             'is_default')
    def is_default(self):
        return self.id == 'index'

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_content')
    def get_content(self):
        """Get the content. Can be used with acquisition to get
        the 'nearest' content."""
        return self.aq_inner


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'content_url')
    def content_url(self):
        """Get content URL."""
        warnings.warn('content_url() will be removed in Silva 2.4. '
                      'Please use @@absolute_url instead on the result of get_content.',
                      DeprecationWarning, stacklevel=2)
        return self.absolute_url()


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_cacheable')
    def is_cacheable(self):
        return 1


InitializeClass(Content)

