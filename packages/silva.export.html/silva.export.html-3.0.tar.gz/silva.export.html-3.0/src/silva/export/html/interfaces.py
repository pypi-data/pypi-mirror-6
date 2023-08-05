# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core.layout.interfaces import ICustomizableLayer, ISilvaLayer
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IBrowserSkinType


class IHTMLExportLayer(ICustomizableLayer):
    """Layer used to export content in HTML.
    """

class IHTMLExportSkin(IHTMLExportLayer, IBrowserSkinType):
    """Base skin to export content in HTML.
    """

class IDefaultHTMLExportSkin(IHTMLExportSkin, ISilvaLayer):
    """Default skin to export content in HTML
    """
    grok.skin(u"Default HTML export")


class IHTMLExportSettings(Interface):
    """Store the settings for the export.
    """
    root = Attribute(u"Export root")
    skin = Attribute(u"Export skin")

    def add_resource(path, target, locals=None):
        """Add an extra resource in the export (used for skin
        resources). ``path`` can be a folder.
        """

    def get_contents():
        """Return an iterator on content to be exported.
        """

    def get_resources():
        """Return an iterator on resources to be added to the
        export. (The one added with ``add_resource``).
        """
