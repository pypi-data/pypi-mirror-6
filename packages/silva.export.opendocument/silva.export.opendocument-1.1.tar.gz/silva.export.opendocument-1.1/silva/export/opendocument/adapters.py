# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.interface import implements
from zope.component import adapts

# Zope 2
import Globals
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.adapters import adapter
from silva.core import interfaces as silva_interfaces
from silva.core.interfaces import adapters as interfaces

from pkg_resources import resource_filename, Requirement
from lxml.etree import ElementTree, XML, XSLT, tostring

from cStringIO import StringIO
from zipfile import ZipFile


def fileResource(name):
    """Return a path to the givem resource/template in the egg.
    """
    req = Requirement.parse('silva.export.opendocument')
    tp = 'silva/export/opendocument/templates/%s' % name
    return resource_filename(req, tp)


class ODFDocument(object):
    """Create an ODF Document from a template, let add ressource
    inside of it.
    """

    def __init__(self, template_name):
       template = open(fileResource(template_name), 'r')
       self._doc = StringIO()
       self._doc.write(template.read())
       self._doc.seek(0)
       self._manifest = []

    def _add(self, name, content):
        archive = ZipFile(self._doc, 'a')
        archive.writestr(name, content)
        archive.close()
        self._doc.seek(0)

    def add(self, name, content, content_type='text/xml'):
        self._add(name, content)
        self._manifest.append((name, content_type,),)

    def download(self):
        new_to_manifest = ""
        for name, content_type in self._manifest:
            new_to_manifest += '<manifest:file-entry manifest:media-type="%s" manifest:full-path="%s"/>\n  ' % (content_type, name)
        template_manifest = open(fileResource('manifest.xml'), 'r').read()
        self._add('META-INF/manifest.xml', template_manifest % new_to_manifest)
        return self._doc.getvalue()

class OpenDocumentExportAdapter(adapter.Adapter):
    """Adapter to export Silva Object to OpenDocument
    """

    implements(interfaces.IContentExporter)

    security = ClassSecurityInfo()

    name = "Open Document (odt)"
    extension = "odt"

    def _getXSLT(self):
        stream = open(fileResource('silva2odt.xslt'), 'r')
        return ElementTree(XML(stream.read()))

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'export')
    def export(self, settings=None):
        from Products.Silva.silvaxml import xmlexport

        # export context to xml
        if settings == None:
            settings = xmlexport.ExportSettings()
        exporter = xmlexport.theXMLExporter
        info = xmlexport.ExportInfo()
        export_root = xmlexport.SilvaExportRoot(self.context)
        xml_export = exporter.exportToString(export_root, settings, info)

        document = ODFDocument('odt_template.zip')
        # Usefull for debug, include the silva export
        #document.add('silva.xml', xml_export)

        for path, id in info.getAssetPaths():
            asset = self.context.restrictedTraverse(path)
            if not silva_interfaces.IImage.providedBy(asset):
                continue
            adapter = interfaces.IAssetData(asset)
            if adapter is not None:
                document.add('Pictures/%s' % asset.id,
                             adapter.getData(),
                             content_type=asset.content_type())

        # now transform the XML
        xml_export = ElementTree(XML(xml_export))
        style_content = XSLT(self._getXSLT())

        content = style_content.apply(xml_export)
        document.add('content.xml', tostring(content))
        return document.download()


Globals.InitializeClass(OpenDocumentExportAdapter)
