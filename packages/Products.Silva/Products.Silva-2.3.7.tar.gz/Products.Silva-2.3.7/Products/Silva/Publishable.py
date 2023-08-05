# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import bisect


# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.icon import get_icon_url
from Products.Silva.SilvaObject import SilvaObject

from five import grok
from silva.core.interfaces.content import (
    IPublishable, INonPublishable, IContent, IVersioning,
    IVersion, IContainer, IPublication, ISilvaObject)
from silva.core.references.interfaces import IReferenceService
from silva.core.smi.interfaces import ISMILayer
from silva.core.smi.interfaces import IPropertiesTabIndex, IEditTabIndex
from silva.core.smi.smi import SMIPortletManager
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import ISilvaURL
from zope import component
from zope.traversing.browser import absoluteURL



class NonPublishable(SilvaObject):
    """Base content which is not a published content in Silva. It
    doesn't appear in navigation, and is not ordered.
    """
    grok.baseclass()
    grok.implements(INonPublishable)



class Publishable(SilvaObject):
    """Base content that can be published and ordered in Silva.
    """
    grok.baseclass()
    grok.implements(IPublishable)

    security = ClassSecurityInfo()

    # ACCESSORS

    # XXX: those two methods is_published and is_approved are only
    # used in VersionedContent. They should move there.
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_published')
    def is_published(self):
        if IVersioning.providedBy(self):
            return self.is_version_published()
        else:
            return 1

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_approved')
    def is_approved(self):
        if IVersioning.providedBy(self):
            return self.is_version_approved()
        else:
            # never be approved if there is no versioning
            return 0

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """Analogous to is_deletable() (?)
        """
        return not self.is_published() and not self.is_approved()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_real_container')
    def get_real_container(self):
        """Get the container, even if we're a container.

        If we're the root object, returns None.

        Can be used with acquisition to get the 'nearest' container.
        """
        return self.get_container()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_document_navigation_links')
    def get_document_navigation_links(self):
        """
        Create a dictionary with top, up, first, previous, next, last links.

        This can be used by Mozilla in the accessibility toolbar.
        """
        # we need get_real_container as we want the container
        # *even if* we are a container ourselves
        container = self.get_real_container()
        # if we're in the root, we can't navigate
        if container is None:
            return {}

        if IContent.providedBy(self) and self.is_default():
            return container.get_document_navigation_links()

        result = { 'up': '..' }
        links = {}
        objects = []
        object_ids = []

        top = self.get_publication()
        if top is not self:
            result['top'] = top#.absolute_url()

        tree = container.get_public_tree(0)
        for depth, obj in tree:
            if obj.meta_type == 'Silva AutoTOC':
                continue
            if obj.meta_type == 'Silva Indexer':
                continue
            object_ids.append(obj.id)
            objects.append(obj)

        # something bad happens
        # could be, that we're calling this method from an Indexer, so
        # return nothing
        try:
            i = object_ids.index(self.id)
        except ValueError:
            return {}

        first = 0
        previous = i - 1
        next = i + 1
        last = len(object_ids) - 1

        if i != first:
            links['first'] = first
        if i != last:
            links['last'] = last
        if previous >= first:
            links['prev'] = previous
        if next <= last:
            links['next'] = next

        for key, value in links.items():
            links[key] = objects[value]#.absolute_url()

        result.update(links)
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_navigation_links')
    def get_navigation_links(self):
        """
        Create a dictionary with top, up, first, previous, next, last links.

        This can be used by Mozilla in the accessibility toolbar.
        """

        top = self.get_publication()
        result = {}
        next = self.get_navigation_next()
        prev = self.get_navigation_prev()
        last = self.get_navigation_last()

        if top is not self:
            result['top'] = top
            result['first'] = top
            result['up'] = ".."


        if last.id != self.id:
            result['last'] = last

        if next is not None:
            result['next'] = next

        if prev is not None:
            result['prev'] = prev

        return result


    def get_navigation_prev(self):
        """ Returns the prev object in the publication tree """
        node = self
        top = self.get_publication()

        if self is top:
            return None

        while 1:
            if node is top:
                return node
            if IContainer.providedBy(node):
                container = node.aq_parent
            container = node.aq_parent
            #objects = container.get_public_tree(0)
            objects = container.get_public_tree_helper(0)
            object_ids = [object.id for depth, object in objects]
            try:
                i = object_ids.index(self.id)
            except ValueError:
                return container

            prev_i = i-1

            # there is no previous in a folder, so check if node is a
            # folder or not
            if prev_i == -1:
                return container
            elif prev_i >= 0 and IContainer.providedBy(objects[prev_i][1]):
                return self._get_last_helper(objects[i-1][1])

            if prev_i >= 0:
                return objects[prev_i][1]

            node = container

    def get_navigation_next(self):
        """ Returns the next object in the Publication tree """
        node = self
        top = self.get_publication()
        if IContainer.providedBy(node):
            #objects = node.get_public_tree(0)
            objects = node.get_public_tree_helper(0)
            if objects:
                return objects[0][1]

        while 1:
            if self is top:
                return None

            container = node.aq_parent
            objects = node.get_public_tree_helper(0)
            object_ids = [object.id for depth, object in objects]
            try:
                i = object_ids.index(self.id)
            except ValueError:
                if not object_ids:
                    self = node
                    node = container
                    continue
                else:
                    return objects[0][1]


            next_i = i+1

            if next_i < len(objects):
                return objects[next_i][1]

            self = node
            node = container

    def get_public_tree_helper(self, depth):
        """ wrapper method for get_public_tree()
            returns the public tree without any publications
        """
        public_tree = []
        tree = self.get_public_tree(depth)
        for item in tree:
            if IPublication.providedBy(item[1]):
                continue
            else:
                public_tree.append(item)

        return public_tree

    def get_navigation_last(self):
        """ Returns the last object in the publication tree """
        node = self.get_publication()
        return self._get_last_helper(node)

    def _get_last_helper(self, root):
        """ returns the last object in a tree """
        node = root
        while 1:
            if IContent.providedBy(node):
                return node
            if IContainer.providedBy(node):
                objects = node.get_public_tree(0)
                if not objects:
                    return node

                node = objects[-1][1]

InitializeClass(Publishable)


class ContentReferencedBy(silvaviews.Viewlet):
    """Report reference usage of this publishable
    """
    grok.context(ISilvaObject)
    grok.layer(ISMILayer)
    grok.order(100)
    grok.view(IPropertiesTabIndex)
    grok.viewletmanager(SMIPortletManager)

    def update(self):
        references = {}
        service = component.getUtility(IReferenceService)
        self.icon_url = get_icon_url(self.context, self.request)
        for reference in service.get_references_to(self.context):
            source = reference.source
            source_versions = []
            if IVersion.providedBy(source):
                source_versions.append(source.id)
                source = source.get_content()

            edit_url = absoluteURL(source, self.request) + '/edit'
            if edit_url in references and source_versions:
                previous_versions = references[edit_url]['versions']
                if previous_versions[-1] > source_versions[0]:
                    bisect.insort_right(
                        previous_versions, source_versions[0])
                    continue
                else:
                    source_versions = previous_versions + source_versions

            source_title = source.get_title_or_id()
            source_url = component.getMultiAdapter(
                (source, self.request), ISilvaURL).preview()
            references[edit_url] = {
                'title': source_title,
                'url': source_url,
                'path': '/'.join(source.getPhysicalPath()),
                'edit_url': edit_url,
                'icon': get_icon_url(source, self.request),
                'versions': source_versions}

        self.references = references.values()
        self.references.sort(key=lambda info: info['title'].lower())

        for info in self.references:
            if info['versions']:
                info['title'] += ' (' + ', '.join(info['versions']) + ')'


class EditContentReferencedBy(ContentReferencedBy):
    grok.view(IEditTabIndex)
