# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Acquisition import aq_parent, aq_chain

from five import grok
from zope.publisher.browser import TestRequest
from zope.traversing.browser import absoluteURL

from silva.core.interfaces import IPublishable, IContainer, IAsset
from silva.core.references.utils import relative_path
from silva.core.views.interfaces import IVirtualSite
from silva.export.html.interfaces import IHTMLExportSettings


class HTMLExportVirtualSite(object):
    grok.implements(IVirtualSite)

    def __init__(self, settings, request):
        self.settings = settings
        self.request = request

    def get_root(self):
        return self.settings.root

    def get_root_url(self):
        return absoluteURL(self.settings.root, self.request)

    def get_site_root(self):
        return self.settings.root.get_root()

    def get_virtual_root(self):
        return None

    def get_virtual_path(self):
        return None


class HTMLContentUrl(object):

    def __init__(self, root, extension='html'):
        if not IContainer.providedBy(root):
            root = aq_parent(root)
        self._origin = root.getPhysicalPath()
        self.extension = extension

    def __call__(self, content):
        if IContainer.providedBy(content):
            path = list(content.getPhysicalPath()) + [
                'index.' + self.extension]
        elif IPublishable.providedBy(content):
            path = list(aq_parent(content).getPhysicalPath()) + [
                content.getId() + '.' + self.extension]
        elif IAsset.providedBy(content):
            path = list(aq_parent(content).getPhysicalPath()) + [
                content.get_filename()]
        else:
            path = content.getPhysicalPath()
        return '/'.join(relative_path(self._origin, path))


class HTMLExportRequest(TestRequest):

    def __init__(self, content, settings):
        super(HTMLExportRequest, self).__init__(skin=settings.skin)
        self._settings = settings
        self.PARENTS = list(aq_chain(content))[:-1]
        self.other = {'PARENTS': self.PARENTS}
        self.getHTMLUrl = HTMLContentUrl(content)


def request_settings(request):
    return request._settings

def virtual_site(request):
    return HTMLExportVirtualSite(request_settings(request), request)

grok.global_adapter(virtual_site, (HTMLExportRequest,), IVirtualSite)
grok.global_adapter(request_settings, (HTMLExportRequest,), IHTMLExportSettings)


class AbsoluteURL(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def url(self, preview=False):
        return self.request.getHTMLUrl(self.context)

    def preview(self):
        return self.url(preview=True)

    __str__ = __call__ = __repr__ = __unicode__ = url

    def breadcrumbs(self):
        return []
