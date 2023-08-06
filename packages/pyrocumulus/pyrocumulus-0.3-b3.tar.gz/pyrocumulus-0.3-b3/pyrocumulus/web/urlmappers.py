# Copyright 2013 Juca Crispim <jucacrispim@gmail.com>

# This file is part of pyrocumulus.

# pyrocumulus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pyrocumulus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pyrocumulus.  If not, see <http://www.gnu.org/licenses/>.

from tornado.web import URLSpec
from pyrocumulus import utils
from pyrocumulus.parsers import get_parser
from pyrocumulus.web.request_handlers import get_rest_handler


class DocumentURLMapper:
    """
    Maps urls for an mongoengine Document. Creates urls like:

    URLSpec('prefix/name/(.*)$', RestHandler, dict(model=document),
             name='full.Name')
    """

    def __init__(self, document, request_handler, prefix=''):
        """
        :param document: A mongoengine Document subclass
        :param request_handler: RequestHandler to map document with
        :param prefix: URL prefix
        :param name: Name to be used in URL pattern. If not name,
        self.document.__name__.lower() will be used.
        """
        self.document = document
        self.name = self.document.__name__.lower()
        self.request_handler = request_handler
        self.prefix = prefix

    @property
    def urls(self):
        return self.get_urls()

    def get_urls(self):
        """
        Returns a list of URLSpec objects to self.document, including its
        EmbeddedDocuments.
        """
        urls = []
        parser = get_parser(self.document)
        parsed_model = parser.parse()
        embedded_documents = parsed_model.get('embedded_documents', [])
        for name, embedded  in embedded_documents.items():
            prefix = self.name
            if self.prefix:
                prefix = '%s/%s' %(self.prefix, prefix)
            mapper = EmbeddedDocumentURLMapper(embedded, self.document,
                                               prefix=prefix, name=name)
            urls += mapper.urls

        pattern = self.get_url_pattern(prefix=self.prefix)
        urlname = self.get_url_name()
        kwargs = self.get_handler_kwargs()
        url = URLSpec(pattern, self.request_handler, kwargs,
                      name=urlname)
        urls.append(url)

        return urls

    def get_url_name(self):
        """
        Get the name for URLSpec
        """
        name = utils.fqualname(self.document)
        return name

    def get_handler_kwargs(self):
        """
        Get the kwargs to be passed to request handler
        """
        return dict(model=self.document)

    def get_url_pattern(self, prefix=''):
        """
        :param prefix: will be inserted in the pattern

        Returns a pattern to be used in the url mapping process.
        """
        pattern = '%s/(.*)' % self.name
        if prefix:
            pattern = '%s/%s' % (prefix, pattern)
        return pattern


class EmbeddedDocumentURLMapper(DocumentURLMapper):
    """
    URLMapper for EmbeddedDocuments. Creates urls like:

    URLSpec('prefix/parent/name/(.*)$', RestHandler, dict(model=document),
             name='full.Name')
    """
    def __init__(self, document, parent_doc, prefix='', name=''):
        """
        :param document: A mongoengine EmbeddedDocument subclass.
        :param parent_doc: A mongoengine Document subclass, the parent doc
        of the EmbeddedDocument.
        :param prefix: URL prefix
        :param name: Name to be used in URL pattern. If not name,
        self.document.__name__.lower() will be used.
        """
        self.document = document
        self.parent_doc = parent_doc
        self.name = name or self.document.__name__.lower()
        self.prefix = prefix
        self.request_handler = get_rest_handler(self.document, self.parent_doc)

    def get_handler_kwargs(self):
        return dict(model=self.document, parent_doc=self.parent_doc)

    def get_url_name(self):
        class_name = self.document.__name__
        name = '%s.%s' % (utils.fqualname(self.parent_doc), class_name)
        return name
