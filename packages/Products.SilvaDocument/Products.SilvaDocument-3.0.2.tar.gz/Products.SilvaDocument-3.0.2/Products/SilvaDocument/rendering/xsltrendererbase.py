# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from StringIO import StringIO
from lxml import etree
import os
import threading

from silva.core.xml import Exporter


class ImportResolver(etree.Resolver):

    def __init__(self, directory):
        self.directory = directory

    def resolve(self, url, id, context):
        if url.startswith("silvabase:"):
            return self.resolve_filename(self.directory + url[10:], context)


class XSLTTransformer(object):

    def __init__(self, path, file_context, import_context=__file__):
        """XSLT-based renderer.

        path - the relative path to use to the XSLT stylesheet

        file_context - the directory or file in the directory to look
                       in. Typically __file__ is passed to look in the
                       module's context.

        import_context - usually this directory: the place to import
                         doc_elements.xslt from.
        """
        path_context = os.path.dirname(os.path.abspath(file_context))
        if os.path.isdir(path_context) and not path_context.endswith('/'):
            path_context += '/'
        import_dir = os.path.dirname(os.path.abspath(import_context))
        if os.path.isdir(import_dir) and not import_dir.endswith('/'):
            import_dir += '/'
        self.__stylesheet_path = os.path.join(path_context, path)
        self.__stylesheet_dir = path_context
        self.__import_dir = import_dir
        # we store stylesheets in a thread-local storage
        self.__local = threading.local()

    def stylesheet(self):
        if not hasattr(self.__local, 'stylesheet'):
            with open(self.__stylesheet_path) as stylesheet:
                parser = etree.XMLParser()
                parser.resolvers.add(ImportResolver(self.__import_dir))
                xslt_doc = etree.parse(stylesheet, parser)
            self.__local.stylesheet = etree.XSLT(xslt_doc)
        return self.__local.stylesheet

    def transform(self, context, request, options={}):
        options.update({'external_rendering': True, 'only_previewable': True})
        exporter = Exporter(context, request, options)
        return self.transform_xml(exporter.getString())

    def transform_xml(self, text):
        style = self.stylesheet()
        doc = etree.parse(StringIO(text))
        result = str(style(doc)).decode('utf-8')
        if result.startswith('<!DOCTYPE'):
            result = result[result.find('>')+1:].strip()
        return result
