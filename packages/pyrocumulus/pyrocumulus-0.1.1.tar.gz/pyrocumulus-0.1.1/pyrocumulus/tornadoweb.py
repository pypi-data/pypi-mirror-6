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


import re
from datetime import datetime
from tornado.web import RequestHandler, HTTPError
from mongoengine.fields import ReferenceField
from mongoengine.errors import ValidationError, NotUniqueError
from pyrocumulus.converters import get_converter


class BaseRestHandler(RequestHandler):
    def initialize(self, model, object_depth=1):
        """
        Called after __init__
        """
        self.model = model
        self.object_depth = object_depth
        self.operations = {'list': self._list_objects,
                           'get': self._get_object,
                           'put': self._put_object,
                           'delete': self._delete_object}
        self.model_reference_fields = self._get_model_reference_fields()

    def prepare(self):
        """
        Called in the beginnig of every request
        """
        self.params = self._prepare_arguments()
        self.callback = self._get_callback()
        self.pagination = self._get_pagination()

    def get(self, operation):
        """
        Called on GET requests
        """
        # operations allowed for this method (get)
        allowed_operations = ['get', 'list']
        operation = operation or 'get'

        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self._call_method_and_write_json(method_to_call)

    def post(self, operation):
        """
        Called on POST requests
        """

        allowed_operations = ['put', 'delete']
        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self._call_method_and_write_json(method_to_call)

    def put(self, operation):
        """
        Called on PUT requests
        """
        allowed_operations = ['put']
        operation = operation or 'put'
        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self._call_method_and_write_json(method_to_call)

    def delete(self, operation):
        """
        Called on DELETE requests
        """
        allowed_operations = ['delete']
        operation = operation or 'delete'
        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self._call_method_and_write_json(method_to_call)

    def _list_objects(self, **kwargs):
        return self.model.objects.filter(**kwargs)

    def _get_object(self, **kwargs):
        return self.model.objects.get(**kwargs)
        
    def _put_object(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        return obj

    def _delete_object(self, **kwargs):
        obj = self._get_object(**kwargs)
        obj.delete()
        return obj

    def _validade_operation(self, operation, allowed_operations):
        if not operation in self.operations.keys():
            raise HTTPError(404)
        if not operation in allowed_operations:
            raise HTTPError(405)
        return self.operations[operation]

    def _prepare_arguments(self):
        """
        Parse request params and create dict containing
        only params to be passed to mongoengine queryset
        get() or filter()
        """
        arguments = {}
        pattern_string = '(\d+)-(\d+)-(\d+)\s(\d+):(\d+):(\d+)'
        datetime_pattern = re.compile(pattern_string)

        for key, value in self.request.arguments.items():
            if isinstance(value, list):
                value = value[0]

            if isinstance(value, bytes):
                value = value.decode()

            is_date = False if not isinstance(value, str) else \
                datetime_pattern.match(value)

            # handling with ReferenceFields. If the param is
            # `thing_id`, and there's a ReferenceField
            # called `thing`, let's try to get an
            # instance of the referenced object
            if key.endswith('_id') and key.split('_id')[0] \
               in self.model_reference_fields.keys():

                key = key.split('_id')[0]
                ref_class = self.model_reference_fields[key]
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

    def _get_callback(self):
        """
        Get callback to be used in jsonp responses
        """
        return self.request.arguments.get('callback')

    def _get_pagination(self):
        """
        Get pagination parameters from requets' arguments
        """
        max_items = int(self.request.arguments.get('max', 10))
        ini = (int(self.request.arguments.get('page', 1)) - 1) * max_items
        end = ini + max_items
        pagination = {'ini': ini, 'end': end}
        return pagination

    def _convert2json(self, obj):
        """
        Converts an object into a json
        """
        converter = get_converter(obj, self.object_depth)
        return converter.to_json()

    def _call_method_and_write_json(self, method_to_call):
        returned = method_to_call(**self.params)
        myjson = self._convert2json(returned)

        self.write(myjson)

    def _get_model_reference_fields(self):
        """
        Creates a dict with {'field_name': ReferecedClass}
        for all ReferenceFields in the model
        """
        fields_names = [i for i in dir(self.model) if not i.startswith('_')
                        or not i == 'objects']
        reference_fields = {}
        for name in fields_names:
            field = getattr(self.model, name)
            is_reference = isinstance(field, ReferenceField)
            if is_reference:
                reference_fields[name] = field.document_type
        return reference_fields


class RestHandler(BaseRestHandler):
    pass
