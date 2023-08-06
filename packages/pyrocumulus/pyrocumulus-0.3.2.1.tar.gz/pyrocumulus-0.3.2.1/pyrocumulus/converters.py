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

import re
import copy
import json
import warnings
from bson.objectid import ObjectId
from datetime import datetime
from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import ReferenceField, ListField, EmbeddedDocumentField
from mongoengine.queryset.manager import QuerySetManager
from pyrocumulus.parsers import get_parser


def get_converter(obj, max_depth=0):
    if isinstance(obj, Document):
        return DocumentConverter(obj, max_depth)
    return QuerySetConverter(obj, max_depth)


def get_request_converter(obj, model):
    return RequestConverter(obj, model)


class BaseConverter:
    """
    Base class for all converters. These converters are
    meant to convert mongoengine objects - Document or
    QuerySet - or an incomming request
    """

    def __init__(self, obj, max_depth=0):
        self.obj = obj
        self.max_depth = max_depth

    def sanitize_dict(self, dict_to_sanitize):
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
                    val = self.sanitize_dict(value)
                    new_dict[key] = val
                elif isinstance(value, list):
                    val = [self.sanitize_dict(v) for v in value]
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
            is_ref = False if is_manager else isinstance(
                getattr(self.obj.__class__, attr), ReferenceField)
            is_list = False if is_manager else isinstance(
                getattr(self.obj.__class__, attr), ListField)
            is_embed = False if is_manager else isinstance(
                getattr(self.obj.__class__, attr), EmbeddedDocumentField)

            if ((callable(obj_attr) or is_manager) or (
                    (is_list or is_ref or is_embed) and self.max_depth == 0)):
                continue

            if is_ref or is_embed:
                converter = self.__class__(obj_attr,
                                           max_depth=self.max_depth-1)
                obj_attr = converter.to_dict()
            elif is_list:
                # is is a ListField, check each one to see if is necessary
                # to convert it.
                ret_list = []
                for item in obj_attr:
                    is_ref = issubclass(type(item), Document)
                    is_embed = issubclass(type(item), EmbeddedDocument)
                    if is_ref or is_embed:
                        converter = type(self)(item,
                                               max_depth=self.max_depth)
                        item = converter.to_dict()
                    ret_list.append(item)
                obj_attr = ret_list

            return_obj[attr] = obj_attr

        return return_obj


    def to_json(self):
        dict_to_convert = self.to_dict()
        dict_to_convert = self.sanitize_dict(dict_to_convert)
        return super(DocumentConverter, self).to_json(dict_to_convert)


class QuerySetConverter(BaseConverter):
    """
    Converts a QuerySet instance into a list of
    dictionaries
    """

    def to_dict(self):
        queryset_list = []
        for document in self.obj:
            converter = DocumentConverter(document, max_depth=self.max_depth)
            obj_dict = converter.to_dict()
            queryset_list.append(obj_dict)
        queryset_dict = {'items': queryset_list,
                         'quantity_items': len(queryset_list)}
        return queryset_dict

    def to_json(self):
        queryset_dict = self.sanitize_dict(self.to_dict())
        return super(QuerySetConverter, self).to_json(queryset_dict)


class RequestConverter(BaseConverter):
    """
    Converts the arguments from the incomming request
    to a dict.
    """

    def __init__(self, obj, model):
        """
        :param model: model from a request handler - a mongoengine document.
        """

        super(RequestConverter, self).__init__(obj)
        self.parsed_model = get_parser(model).parse()

    def to_json(self):
        raise NotImplementedError

    def to_dict(self):
        """
        Parse request params and create dict containing
        only params to be passed to mongoengine queryset
        get() or filter()
        """

        # deform send some control keys which conflicts
        # with mongoengine, so we remove it.
        invalid_keys = ['_charset_', '__formid__']
        arguments = {}
        for key, value in self.obj.items():
            if key in invalid_keys:
                continue

            is_reference = self._is_reference(key)
            is_list = self._is_listfield(key)

            # keep as a list only what is a ListField
            if isinstance(value, list) and not is_list:
                value = value[0]

            # converting to unicode
            if isinstance(value, bytes):
                value = value.decode()

            # converting list items to unicode
            if is_list:
                new_list = []
                for item in value:
                    if isinstance(item, bytes):
                        item = item.decode()
                    new_list.append(item)
                value = new_list

            is_date = self._is_date(value)

            # handling with ReferenceFields. If the param is
            # `thing_id`, and there's a ReferenceField
            # called `thing`, let's try to get an
            # instance of the referenced object
            if is_reference:
                key = key.split('_id')[0]
                ref_class = self.parsed_model['reference_fields'][key]
                try:
                    value = ref_class.objects.get(id=value)
                except ref_class.DoesNotExist:
                    value = None

            # handling with datetime. The value must be a string like
            # YYYY-mm-dd HH:MM:SS. Will be turned into a datetime object
            elif is_date:
                datelist = [int(i) for i in is_date.groups()]
                value = datetime(*datelist)

            arguments[key] = value

        return arguments

    def _is_date(self, value):
        pattern_string = '(\d+)-(\d+)-(\d+)\s(\d+):(\d+):(\d+)'
        datetime_pattern = re.compile(pattern_string)

        is_date = False if not isinstance(value, str) else \
            datetime_pattern.match(value) or False
        return is_date

    def _is_reference(self, key):
        if key.endswith('_id') and key.split('_id')[0] \
           in self.parsed_model['reference_fields'].keys():
            return True
        return False

    def _is_listfield(self, key):
        return key in self.parsed_model['list_fields'].keys()
