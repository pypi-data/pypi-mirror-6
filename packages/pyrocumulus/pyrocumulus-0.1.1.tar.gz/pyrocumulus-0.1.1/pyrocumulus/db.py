#-*- coding: utf-8 -*-

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


from mongoengine import connect
from pyrocumulus.conf import get_settings_module


class MongoConnection(object):
    def __init__(self, name=None, host=None, port=None, db='default'):
        if not (name or host or port):
            settings = get_settings_module().DATABASE[db]
        else:
            settings = {}

        self.name = name or settings.get('NAME')
        self.host = host or settings.get('HOST')
        self.port = port or settings.get('PORT')
        self.connection = None

    def connect(self):
        self.connection = connect(self.name, host=self.host, port=self.port)
