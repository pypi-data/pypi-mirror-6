# -*- coding: utf-8 -*-
# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope.component import getUtility

# Zope 2
from Acquisition import aq_inner, aq_base
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from zExceptions import Unauthorized

# Silva
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from Products.Silva import SilvaPermissions

from zeam.form.base.fields import Fields
from zeam.form.silva.form import SMIAddForm
from zeam.form.silva.form import SMIEditForm

from silva.core import conf as silvaconf
from silva.core.conf.interfaces import IIdentifiedContent
from silva.core.interfaces import (
    IContainer, IContent, IGhost, IGhostFolder, IGhostAware, IGhostVersion)
from silva.core.references.reference import Reference, get_content_id
from silva.core.references.interfaces import IReferenceService
from silva.core.views import views as silvaviews
from silva.translations import translate as _


class GhostBase(object):
    """baseclass for Ghosts (or Ghost versions if it's versioned)
    """
    security = ClassSecurityInfo()

    # status codes as returned by get_link_status
    # NOTE: LINK_FOLDER (and alike) must *only* be returned if it is an error
    # for the link to point to a folder. If it is not an error LINK_OK must
    # be returned.
    LINK_OK = None   # link is ok
    LINK_EMPTY = 1   # no link entered (XXX this cannot happen)
    LINK_VOID = 2    # object pointed to does not exist
    LINK_FOLDER = 3  # link points to folder
    LINK_GHOST = 4   # link points to another ghost
    LINK_NO_CONTENT = 5 # link points to something which is not a content
    LINK_CONTENT = 6 # link points to content
    LINK_NO_FOLDER = 7 # link doesn't point to a folder
    LINK_CIRC = 8 # Link results in a ghost haunting itself

    # those should go away
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Don't do anything.
        """
        pass

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title')
    def get_title(self):
        """Get title.
        """
        content = self.get_haunted()
        if content is None:
            return ("Ghost target is broken")
        else:
            return content.get_title()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_editable')
    def get_title_editable(self):
        """Get title.
        """
        content = self.get_haunted()
        if content is None:
            return ("Ghost target is broken")
        else:
            return content.get_title_editable()

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """title comes from haunted object
        """
        return False

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short title.
        """
        content = self.get_haunted()
        if content is None:
            return ("Ghost target is broken")
        else:
            short_title = content.get_short_title()
        if not short_title:
            return self.get_title()
        return short_title
    # /those should go away

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_haunted')
    def set_haunted(self, content):
        """ Set the content as the haunted object
        """
        service = getUtility(IReferenceService)
        reference = service.get_reference(
            aq_inner(self), name=u"haunted", add=True)
        if not isinstance(content, int):
            content = get_content_id(content)
        reference.set_target_id(content)

    security.declareProtected(SilvaPermissions.View, 'get_haunted')
    def get_haunted(self):
        service = getUtility(IReferenceService)
        reference = service.get_reference(
            aq_inner(self), name=u"haunted", add=True)
        return reference.target

    security.declareProtected(SilvaPermissions.View, 'get_link_status')
    def get_link_status(self):
        """return an error code if this version of the ghost is broken.
        returning None means the ghost is Ok.
        """
        content = self.get_haunted()
        if content is None:
            return self.LINK_EMPTY
        if IContainer.providedBy(content):
            return self.LINK_FOLDER
        if not IContent.providedBy(content):
            return self.LINK_NO_CONTENT
        if IGhostAware.providedBy(content):
            return self.LINK_GHOST
        return self.LINK_OK


class Ghost(CatalogedVersionedContent):
    __doc__ = _("""Ghosts are special documents that function as a
       placeholder for an item in another location (like an alias,
       symbolic link, shortcut). Unlike a hyperlink, which takes the
       Visitor to another location, a ghost object keeps the Visitor in the
       current publication, and presents the content of the ghosted item.
       The ghost inherits properties from its location (e.g. layout
       and stylesheets).
    """)

    meta_type = "Silva Ghost"
    security = ClassSecurityInfo()

    grok.implements(IGhost)
    silvaconf.icon('icons/silvaghost.gif')
    silvaconf.versionClass('GhostVersion')

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_title_editable')
    def get_title_editable(self):
        """Get title for editable or previewable use
        """
        # Ask for 'previewable', which will return either the 'next version'
        # (which may be under edit, or is approved), or the public version,
        # or, as a last resort, the closed version.
        # This to be able to show at least some title in the Silva edit
        # screens.
        previewable = self.get_previewable()
        if previewable is None:
            return "[No title available]"
        return previewable.get_title_editable()

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """title comes from haunted object
        """
        return False

    security.declarePrivate('getLastVersion')
    def getLastVersion(self):
        """returns `latest' version of ghost

            ghost: Silva Ghost intance
            returns GhostVersion
        """
        version_id = self.get_public_version()
        if version_id is None:
            version_id = self.get_next_version()
        if version_id is None:
            version_id = self.get_last_closed_version()
        version = getattr(self, version_id)
        return version

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'is_version_published')
    def is_version_published(self):
        public_id = self.get_public_version()
        if not public_id:
            return False
        public = getattr(self, public_id)
        haunted = public.get_haunted()
        if haunted is None:
            return False
        return haunted.is_published()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_modification_datetime')
    def get_modification_datetime(self, update_status=1):
        """Return modification datetime."""
        super_method = Ghost.inheritedAttribute(
            'get_modification_datetime')
        content = self.getLastVersion().get_haunted()

        if content is not None:
            return content.get_modification_datetime(update_status)
        else:
            return super_method(self, update_status)


InitializeClass(Ghost)


class GhostVersion(GhostBase, CatalogedVersion):
    """Ghost version.
    """
    meta_type = 'Silva Ghost Version'
    grok.implements(IGhostVersion)

    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
       target = self.get_haunted()
       if target is not None:
           public_version = target.get_viewable()
           if public_version and hasattr(aq_base(public_version), 'fulltext'):
               return public_version.fulltext()
       return ""


class IGhostSchema(IIdentifiedContent):

    haunted = Reference(IContent,
            title=_(u"target"),
            description=_(u"The silva object the ghost is mirroring."),
            required=True)


class GhostAddForm(SMIAddForm):
    """Add form for a ghost
    """
    grok.name(u"Silva Ghost")
    grok.context(IGhost)

    fields = Fields(IGhostSchema)

    def _add(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addGhost(
            data['id'], 'Ghost', haunted=data['haunted'])


class GhostEditForm(SMIEditForm):
    """ Edit form for Ghost
    """
    grok.context(IGhost)
    fields = Fields(IGhostSchema).omit('id')


class GhostView(silvaviews.View):
    grok.context(IGhost)

    broken_message = _(u"This 'ghost' document is broken. "
                       u"Please inform the site manager.")

    def render(self):
        # FIXME what if we get circular ghosts?
        self.request.other['ghost_model'] = aq_inner(self.context)
        try:
            content = self.content.get_haunted()
            if content is None:
                return self.broken_message
            if content.get_viewable() is None:
                return self.broken_message
            permission = self.is_preview and 'Read Silva content' or 'View'
            if getSecurityManager().checkPermission(permission, content):
                return content.view()
            raise Unauthorized(
                u"You do not have permission to "
                u"see the target of this ghost")
        finally:
            del self.request.other['ghost_model']


def ghost_factory(container, identifier, target):
    """add new ghost to container

        container: container to add ghost to (must be acquisition wrapped)
        id: (str) id for new ghost in container
        target: object to be haunted (ghosted), acquisition wrapped
        returns created ghost

        actual ghost created depends on haunted object
        on IContainer a GhostFolder is created
        on IVersionedContent a Ghost is created
    """
    factory = container.manage_addProduct['Silva']
    if IContainer.providedBy(target):
        if IGhostFolder.providedBy(target):
            target = target.get_hauted()
        factory = factory.manage_addGhostFolder
    elif IContent.providedBy(target):
        if IGhost.providedBy(target):
            target = target.getLastVersion().get_haunted()
        factory = factory.manage_addGhost
    factory(identifier, None, haunted=target)
    return getattr(container, identifier)
