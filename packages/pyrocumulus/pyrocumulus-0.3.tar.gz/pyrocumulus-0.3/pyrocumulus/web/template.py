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
from deform import ZPTRendererFactory
from pyrocumulus.conf import settings


class Renderer(ZPTRendererFactory):
    """
    Renderer with extra directories for templates
    """

    def __init__(self):
        deform_templates = resource_filename('deform', 'templates')
        pyrocumulus_templates = resource_filename(
            'pyrocumulus.web', 'templates')
        search_path = (pyrocumulus_templates, deform_templates)
        super(Renderer, self).__init__(search_path)


def context():
    static_url = settings.STATIC_URL
    return {'static_url': static_url}

renderer = Renderer()
