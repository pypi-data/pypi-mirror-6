# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import warnings

# Zope 3
from five import grok
from zope import component
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.container.interfaces import IObjectMovedEvent
from zope.app.container.interfaces import IObjectRemovedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from OFS.interfaces import IObjectWillBeRemovedEvent

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.SilvaObject import TitledObject
from Products.SilvaMetadata.Exceptions import BindingError
from Products.SilvaMetadata.interfaces import IMetadataService

from silva.core.interfaces import IVersion, ICatalogedVersion
from silva.core.services.interfaces import ICataloging


class Version(TitledObject, SimpleItem):

    grok.implements(IVersion)

    security = ClassSecurityInfo()

    object_type = 'versioned_content'

    def __init__(self, id):
        self.id = id
        self._v_creation_datetime = DateTime()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_renderer_name')
    def get_renderer_name(self):
        """Get the name of the renderer selected for object.

        Returns None if default is used.
        """
        return getattr(self, '_renderer_name', None)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'version_status')
    def version_status(self):
        """Returns the status of the current version
        Can be 'unapproved', 'approved', 'public', 'last_closed' or 'closed'
        """
        status = None
        unapproved_version = self.get_unapproved_version(0)
        approved_version = self.get_approved_version(0)
        public_version = self.get_public_version(0)
        previous_versions = self.get_previous_versions()
        if unapproved_version and unapproved_version == self.id:
            status = "unapproved"
        elif approved_version and approved_version == self.id:
            status = "approved"
        elif public_version and public_version == self.id:
            status = "public"
        else:
            if previous_versions and previous_versions[-1] == self.id:
                status = "last_closed"
            elif self.id in previous_versions:
                status = "closed"
            else:
                # this is a completely new version not even registered
                # with the machinery yet
                status = 'unapproved'
        return status

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'object_path')
    def object_path(self):
        """Returns the physical path of the object
        (for identification-purposes)
        """
        return self.aq_inner.aq_parent.getPhysicalPath()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'version')
    def version(self):
        """Returns the version
        """
        return (self.id,
                self.publication_datetime(),
                self.expiration_datetime())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'object')
    def object(self):
        """Returns the object this version belongs to
        """
        warnings.warn('object() will be removed in Silva 2.4. '
                      'Please use get_content instead.',
                      DeprecationWarning, stacklevel=2)
        return self.aq_inner.aq_parent


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'object')
    def get_version(self):
        """Returns itself. Used by acquisition to get the
           neared version.
        """
        return self.aq_inner


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'publication_datetime')
    def publication_datetime(self):
        """Returns the publication_datetime of this version (if any)
        """
        status = self.version_status()
        if status == 'closed' or status == 'last_closed':
            return None
        else:
            return getattr(self,
                           'get_%s_version_publication_datetime' % status)(0)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'expiration_datetime')
    def expiration_datetime(self):
        """Returns the expiration_datetime of this version (if any)
        """
        status = self.version_status()
        if status == 'closed' or status == 'last_closed':
            return None
        else:
            return getattr(self,
                           'get_%s_version_expiration_datetime' % status)(0)

InitializeClass(Version)


class CatalogedVersion(Version):
    """Base class for cataloged version objects"""

    grok.implements(ICatalogedVersion)

    # XXX: TODO ICataloging for ICataloged Version
    # def index_object(self):
    #     """Index"""
    #     catalog = getattr(self, 'service_catalog', None)
    #     if catalog is not None:
    #         catalog.catalog_object(self, self.getPath())
    #         if self.version_status() in ('unapproved','approved','public'):
    #             #search for Ghost objects in the catalog
    #             # that have this object's path as the haunted_path
    #             # these Ghost objects need to be reindexed
    #             # NOTE: this will change published and unpublished
    #             # Ghost versions.
    #             res = catalog(haunted_path={'query':(self.get_content().getPhysicalPath(),)})
    #             for r in res:
    #                 r.getObject().index_object()


    # def reindex_object(self):
    #     """Reindex."""
    #     catalog = getattr(self, 'service_catalog', None)
    #     if catalog is None:
    #         return
    #     path = self.getPath()
    #     catalog.uncatalog_object(path)
    #     catalog.catalog_object(self, path)
    #     if self.version_status() in ('unapproved','approved','public'):
    #         #search for Ghost objects in the catalog
    #         # that have this object's path as the haunted_path
    #         # these Ghost objects need to be reindexed
    #         # NOTE: this will change published and unpublished
    #         # Ghost versions.
    #         res = catalog(haunted_path={'query':(self.get_content().getPhysicalPath(),)})
    #         for r in res:
    #             r.getObject().index_object()


InitializeClass(CatalogedVersion)

def _(s): pass
_i18n_markers = (_('unapproved'), _('approved'), _('last_closed'),
                 _('closed'), _('draft'), _('pending'), _('public'),)


@grok.subscribe(IVersion, IObjectModifiedEvent)
def version_modified(version, event):
    # This version have been modified
    version.get_content().sec_update_last_author_info()


@grok.subscribe(ICatalogedVersion, IObjectWillBeRemovedEvent)
def catalog_version_removed(version, event):
    if version != event.object:
        # Only interested about version removed by hand.
        return
    ICataloging(version).unindex()


@grok.subscribe(IVersion, IObjectMovedEvent)
def version_moved(version, event):
    if version != event.object or IObjectRemovedEvent.providedBy(event):
        return
    timings = {}
    ctime = getattr(version, '_v_creation_datetime', None)
    if ctime is None:
        return
    try:
        service_metadata = component.getUtility(IMetadataService)
        binding = service_metadata.getMetadata(version)
    except BindingError:
        return
    if binding is None:
        return
    for elem in ('creationtime', 'modificationtime'):
        old = binding.get('silva-extra', element_id=elem)
        if old is None:
            timings[elem] = ctime
    binding.setValues('silva-extra', timings)
