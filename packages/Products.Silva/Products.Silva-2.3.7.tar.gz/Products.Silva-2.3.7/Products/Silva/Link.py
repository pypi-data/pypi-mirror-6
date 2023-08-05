# Copyright (c) 2003-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope import schema, interface
from zope.traversing.browser import absoluteURL
from zope.component import getUtility

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from App.class_init import InitializeClass

# Silva
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.conf.interfaces import ITitledContent
from silva.core.references.reference import Reference, get_content_id
from silva.core.references.interfaces import IReferenceService
from silva.core.views import views as silvaviews
from silva.translations import translate as _

from zeam.form import silva as silvaforms


class Link(CatalogedVersionedContent):
    __doc__ = _("""A Silva Link makes it possible to create links that show up
    in navigation or a Table of Contents. The links can be absolute or relative.
    Absolute links go to external sites while relative links go to content
    within Silva.
    """)

    meta_type = "Silva Link"

    grok.implements(interfaces.ILink)
    silvaconf.icon('www/link.png')
    silvaconf.versionClass('LinkVersion')


class LinkVersion(CatalogedVersion):
    security = ClassSecurityInfo()

    meta_type = "Silva Link Version"

    grok.implements(interfaces.ILinkVersion)

    _url = None
    _relative = False

    security.declareProtected(SilvaPermissions.View, 'get_relative')
    def get_relative(self):
        return self._relative

    security.declareProtected(SilvaPermissions.View, 'get_target')
    def get_target(self):
        service = getUtility(IReferenceService)
        reference = service.get_reference(
            aq_inner(self), name=u'link', add=True)
        return reference.target

    security.declareProtected(SilvaPermissions.View, 'get_url')
    def get_url(self):
        return self._url

    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_relative')
    def set_relative(self, relative):
        self._relative = relative

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_target')
    def set_target(self, target):
        service = getUtility(IReferenceService)
        reference = service.get_reference(
            aq_inner(self), name=u'link', add=True)
        if not isinstance(target, int):
            target = get_content_id(target)
        reference.set_target_id(target)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_url')
    def set_url(self, url):
        self._url = url


InitializeClass(LinkVersion)


class ILinkSchema(interface.Interface):

    url = schema.URI(
        title=_(u"url"),
        description=_(u"If the link goes to an external resource, fill in the "
                      u"location, including the protocol, e.g. 'http://'."),
        required=False)

    relative = schema.Bool(
        title=_(u"relative link"),
        description=_(u"If the link goes to content in Silva, put a checkmark "
                      u"here and lookup the target below."),
        default=False,
        required=True)

    target = Reference(interfaces.ISilvaObject,
        title=_("target of relative link"),
        description=_(u"Make a reference to internal content by looking it up. "
                      u"Click the search icon to choose a target."),
        required=False)

    @interface.invariant
    def url_validation(content):
        if content.relative and not content.target:
            raise interface.Invalid(
                _("Relative link selected without target."))
        if not content.relative and not content.url:
            raise interface.Invalid(
                _("Absolute link selected without URL."))


class LinkAddForm(silvaforms.SMIAddForm):
    """Add form for a link.
    """
    grok.context(interfaces.ILink)
    grok.name(u'Silva Link')

    fields = silvaforms.Fields(ITitledContent, ILinkSchema)


class LinkEditForm(silvaforms.SMIEditForm):
    """Edit form for a link.
    """
    grok.context(interfaces.ILink)

    fields = silvaforms.Fields(ILinkSchema).omit('id')


class LinkView(silvaviews.View):
    """Render a link.
    """
    grok.context(interfaces.ILink)

    def update(self):
        self.url = None
        if self.content.get_relative():
            self.url = absoluteURL(self.content.get_target(), self.request)
        else:
            self.url = self.content.get_url()
        if not self.is_preview:
            self.redirect(self.url)

    def render(self):
        return u'Link &laquo;%s&raquo; redirects to: <a href="%s">%s</a>' % (
            self.content.get_title(), self.url, self.url)
