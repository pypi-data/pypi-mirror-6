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


import copy
import json
import warnings
from bson.objectid import ObjectId
from datetime import datetime
from mongoengine import Document
from mongoengine.fields import ReferenceField
from mongoengine.queryset.manager import QuerySetManager


def get_converter(obj, max_depth=0):
    if isinstance(obj, Document):
        return DocumentConverter(obj, max_depth)
    return QuerySetConverter(obj, max_depth)


class BaseConverter(object):
    """
    Base class for all converters. These converters are
    meant to convert mongoengine objects - Document or
    QuerySet
    """

    def __init__(self, obj, max_depth=0):
        self.obj = obj
        self.max_depth = max_depth

    def _sanitize_dict(self, dict_to_sanitize):
        """
        Handle values which can't be serialized,
        like datetime.datetime.now() and ObjectId()
        """
        new_dict = copy.copy(dict_to_sanitize)
        for key, value in dict_to_sanitize.items():
            try:
                val = json.dumps(value)
            except TypeError:
                if isinstance(value, datetime):
                    val = value.strftime('%Y-%m-%d %H:%M:%S')
                    new_dict[key] = val
                elif isinstance(value, ObjectId):
                    val = str(value)
                    new_dict[key] = val
                elif isinstance(value, dict):
                    val = self._sanitize_dict(value)
                    new_dict[key] = val
                else:
                    warnings.warn('Could not serialize %s. Skipping it' % key,
                                  RuntimeWarning)
                    del new_dict[key]
        return new_dict

    def to_json(self, obj_to_convert):
        return json.dumps(obj_to_convert)


class DocumentConverter(BaseConverter):
    """
    Converts a mongoengine Document subclass
    into a dict
    """

    def to_dict(self):
        return_obj = {}
        obj_attrs = [attr for attr in dir(self.obj)
                     if not attr.startswith('_')]
        for attr in obj_attrs:
            obj_attr = getattr(self.obj, attr)
            is_manager = isinstance(obj_attr, QuerySetManager)
            is_reference = False if is_manager else isinstance(
                getattr(self.obj.__class__, attr), ReferenceField)

            if ((callable(obj_attr) or is_manager) or (
                    is_reference and self.max_depth == 0)):
                continue

            if is_reference:
                converter = self.__class__(obj_attr,
                                           max_depth=self.max_depth-1)
                obj_attr = converter.to_dict()

            return_obj[attr] = obj_attr

        return return_obj

    def to_json(self):
        dict_to_convert = self.to_dict()
        dict_to_convert = self._sanitize_dict(dict_to_convert)
        return super(DocumentConverter, self).to_json(dict_to_convert)


class QuerySetConverter(BaseConverter):
    """
    Converts a QuerySet instance into a list of
    dictionaries
    """

    def to_list(self):
        return_obj = []
        for document in self.obj:
            converter = DocumentConverter(document, max_depth=self.max_depth)
            obj_dict = converter.to_dict()
            return_obj.append(obj_dict)
        return return_obj

    def to_json(self):
        list_to_convert = self.to_list()
        list_to_convert = [self._sanitize_dict(i) for i in list_to_convert]
        return super(QuerySetConverter, self).to_json(list_to_convert)
