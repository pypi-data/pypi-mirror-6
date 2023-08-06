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
from importlib import import_module
from tornado.web import Application as TornadoApplication
from tornado.web import URLSpec
from pyrocumulus.conf import settings
from pyrocumulus.web.urlmappers import DocumentURLMapper
from pyrocumulus.web.request_handlers import get_rest_handler
from pyrocumulus.web.request_handlers import StaticFileHandler


class Application(TornadoApplication):
    def __init__(self, *models, url_prefix, handlerfactory, extra_urls=[]):
        self.models = models
        self.url_prefix = url_prefix
        self.handlerfactory = handlerfactory
        self.extra_urls = extra_urls
        tornado_opts = getattr(settings, 'TORNADO_OPTS', {})
        super(Application, self).__init__(self.urls, **tornado_opts)

    @property
    def urls(self):
        """
        Returns all the url, including the extra urls passed in the
        constructor
        """
        urls = self.get_urls()
        urls += self.extra_urls
        return urls

    def get_urls(self):
        """
        Returns the urls without the extra ones.
        """
        urls = []
        for document in self.models:
            request_handler = self.handlerfactory(document)
            mapper = DocumentURLMapper(document, request_handler,
                                       self.url_prefix)
            urls += mapper.urls
        return urls


class RestApplication(Application):
    def __init__(self, *models, url_prefix='/api'):
        super(RestApplication, self).__init__(*models, url_prefix=url_prefix,
                                              handlerfactory=get_rest_handler)


def get_main_application():
    """
    Returns an Application instance to be used as the main one.
    It looks uses all applications listed in the APPLICATIONS
    settings variable.

    Using the urls of these applications, creates a new
    `tornado.web.application.Application`
    instance with all urls foundd in the applications.
    """

    urls = []
    for app in settings.APPLICATIONS:
        urls += _get_application_urls(app)

    tornado_opts = getattr(settings, 'TORNADO_OPTS', {})
    main_app = TornadoApplication(urls, tornado_opts)
    # ouch!
    main_app.urls = urls

    return main_app

def _get_application_urls(app_name):
    """
    Returns a list of urls to a given application name.
    It must be a fully qualified name for the application.
    """
    module_name, app_name = app_name.rsplit('.', 1)
    urls = []
    try:
        module = import_module(module_name)
        application = getattr(module, app_name)
        if application:
            urls += application.urls
    except ImportError:
        pass

    return urls
