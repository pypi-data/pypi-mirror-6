# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from cStringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED
import logging
import os

from five import grok
from zope import schema
from zope.component import getMultiAdapter, getUtility, getUtilitiesFor
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from silva.core.interfaces import IAsset, IAssetPayload
from silva.core.interfaces import IPublishable, IContainer, IContentExporter
from silva.core.interfaces.errors import ExternalReferenceError
from silva.core.references.interfaces import IReferenceService
from silva.core.services.utils import walk_silva_tree
from silva.export.html.interfaces import IHTMLExportSkin, IHTMLExportSettings
from silva.export.html.url import HTMLExportRequest, HTMLContentUrl
from silva.translations import translate as _

logger = logging.getLogger('silva.export.html')


class HTMLExportSettings(object):
    grok.implements(IHTMLExportSettings)

    def __init__(self, root, skin):
        self.root = root
        self.skin = skin
        self._resources = {}

    def add_resource(self, target, path=None, where=None):
        parts = []
        if where is not None:
            parts.append(os.path.dirname(where['__file__']))
            parts.append('static')
        if path is not None:
            parts.append(path)
        if not parts:
            raise ValueError(u'Empty path')
        target_path = os.path.join(*parts)
        if self._resources.get(target, target_path) != target_path:
            # We make sure we don't override this with a different path.
            raise ValueError(target)
        self._resources[target] = target_path

    def get_contents(self):
        return walk_silva_tree(self.root, requires=IPublishable)

    def get_resources(self):
        return self._resources.items()


class Exporter(object):

    def __init__(self, settings, archive):
        self.settings = settings
        self.archive = archive
        self.references = []
        self.get_references = getUtility(IReferenceService).get_references_from
        self.get_archive_name = HTMLContentUrl(settings.root)

    def export_content(self):
        for content in self.settings.get_contents():
            if IContainer.providedBy(content):
                continue
            viewable = content.get_viewable()
            if viewable is not None:
                self.archive.writestr(
                    self.get_archive_name(content),
                    getMultiAdapter(
                        (content, HTMLExportRequest(content, self.settings)),
                        name='index.html')().encode('utf-8'))
                self.references.extend(self.get_references(viewable))

    def export_assets(self):
        seen = set()
        root = self.settings.root
        for reference in self.references:
            target = reference.target
            if target is None or not IAsset.providedBy(target):
                continue
            if not reference.is_target_inside_container(root):
                raise ExternalReferenceError(
                    _(u"External references"), root, reference.target, root)
            path = self.get_archive_name(target)
            if path in seen:
                continue
            seen.add(path)
            payload = IAssetPayload(target).get_payload()
            if payload is not None:
                self.archive.writestr(path, payload)

    def export_resources(self):
        add = self.archive.write
        for target, origin in self.settings.get_resources():
            if not os.path.isdir(origin):
                add(origin, target)
                continue
            for dirpath, dirnames, filenames in os.walk(origin):
                for filename in filenames:
                    fullname = os.path.join(dirpath, filename)
                    add(fullname,
                        os.path.join(
                            target, os.path.relpath(fullname, dirpath)))

    def export(self):
        self.export_content()
        self.export_assets()
        self.export_resources()


@grok.provider(IContextSourceBinder)
def html_skin(context):
    terms = []
    for name, skin in getUtilitiesFor(IBrowserSkinType):
        if skin.extends(IHTMLExportSkin):
            terms.append(SimpleTerm(
                    value=skin, token=skin.__identifier__, title=name))
    return SimpleVocabulary(terms)


class IExportOptions(Interface):
    html_skin = schema.Choice(
        title=_("HTML export skin"),
        source=html_skin,
        required=True)


class HTMLExporter(grok.Adapter):
    """Export content to HTML.
    """
    grok.provides(IContentExporter)
    grok.context(IPublishable)
    grok.name('html')

    name = "HTML (zip)"
    extension = "zip"
    options = IExportOptions

    def export(self, html_skin, **options):
        output = StringIO()
        archive = ZipFile(output, "w", ZIP_DEFLATED)
        Exporter(HTMLExportSettings(self.context, html_skin), archive).export()
        archive.close()
        return output.getvalue()
