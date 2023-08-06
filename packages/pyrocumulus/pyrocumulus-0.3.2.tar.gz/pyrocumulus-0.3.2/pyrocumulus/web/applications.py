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

from pkg_resources import resource_filename
from tornado.web import Application, URLSpec
from pyrocumulus.conf import settings
from pyrocumulus.web.urlmappers import DocumentURLMapper
from pyrocumulus.web.request_handlers import get_rest_handler
from pyrocumulus.web.request_handlers import StaticFileHandler


class BaseApplication:
    def __init__(self, *models, prefix, handlerfactory, urls=[]):
        self.models = models
        self.prefix = prefix
        self.handlerfactory = handlerfactory
        self.urls = urls or []

    def get_tornado_app(self):
        return Application(self.urls, debug=True)

    def get_urls(self):
        if self._urls:
            return self._urls

        for document in self.models:
            request_handler = self.handlerfactory(document)
            mapper = DocumentURLMapper(document, request_handler, self.prefix)
            self._urls += mapper.urls
        return self._urls

    def set_urls(self, urls):
        self._urls = urls

    urls = property(get_urls, set_urls)


class RestApplication(BaseApplication):
    def __init__(self, *models, prefix='/api'):
        super(RestApplication, self).__init__(*models, prefix=prefix,
                                              handlerfactory=get_rest_handler)
