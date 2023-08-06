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

from tornado.web import Application
from pyrocumulus.parsers import get_parser
from pyrocumulus.web.request_handlers import (RestHandler,
                                              EmbeddedDocumentHandler)
from pyrocumulus.web.urlmappers import DocumentURLMapper


class RestApplication(Application):
    def __init__(self, *models, prefix='/api'):
        self.models = models
        self.prefix = prefix
        super(RestApplication, self).__init__(self.urls, debug=True)

    @property
    def urls(self):
        urls = []
        for document in self.models:
            mapper = DocumentURLMapper(document, RestHandler, self.prefix)
            urls += mapper.urls
        return urls
