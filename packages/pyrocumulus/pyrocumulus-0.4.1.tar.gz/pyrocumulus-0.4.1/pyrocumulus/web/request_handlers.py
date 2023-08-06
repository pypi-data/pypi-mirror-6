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

import os
import json
from mongoengine import Document, EmbeddedDocument
from tornado.web import RequestHandler, HTTPError
from tornado.web import StaticFileHandler as StaticFileHandlerTornado
from pyrocumulus.converters import get_converter, get_request_converter
from pyrocumulus.parsers import get_parser
from pyrocumulus.exceptions import PyrocumulusException


class BaseRequestHandler(RequestHandler):
    """
    Base request handler for all handlers used
    for automatic api creation.
    """

    def initialize(self, model, cors_origins=None):
        """
        Method called after the class' constructor. Initializes
        the model and parses it.

        :param model: mongoengine Document subclass
        :param cors_origin: Value to "Access-Control-Allow-Origin" header.
                            If not cors_origin, cors is disabled.
        """
        self.model = model
        parser = get_parser(self.model)
        self.parsed_model = parser.parse()
        self.model_reference_fields = self.parsed_model['reference_fields']
        self.model_embedded_documents = self.parsed_model['embedded_documents']
        self.model_list_fields = self.parsed_model['list_fields']

        self.cors_origins = cors_origins
        self.cors_enabled = True if self.cors_origins else False
        if self.cors_enabled:
            self._enable_cors()

    def prepare(self):
        """
        Method called in the beginnig of every request.
        Initializes the params to be passed to self.model.objects.
        """
        self.params = self._prepare_arguments()

    def _prepare_arguments(self):
        """
        Parse request params and create dict containing
        only params to be passed to mongoengine queryset
        get() or filter()
        """
        converter = get_request_converter(self.request.arguments, self.model)
        return converter.to_dict()

    def _enable_cors(self):
        self.set_header("Access-Control-Allow-Origin", self.cors_origins)

    def get(self):  # pragma: no cover
        """
        Method called on GET requests.

        Subclasses must implement it.
        """

        raise NotImplementedError

    def post(self):  # pragma: no cover
        """
        Method called on POST requests.

        Subclasses must implement it.
        """

        raise NotImplementedError

    def put(self):  # pragma: no cover
        """
        Method called on PUT requests.

        Subclasses must implement it.
        """

        raise NotImplementedError

    def delete(self):  # pragma: no cover
        """
        Method called on DELETE requests.

        Subclasses must implement it.
        """

        raise NotImplementedError

    def options(self):  # pragma: no cover
        """
        Method called on OPTIONS requests.

        Subclasses must implement it.
        """

        raise NotImplementedError

    @classmethod
    def embeddedhandler(cls):  # pragma no cover
        """
        Returns the request handler for embedded documents
        """

        raise NotImplementedError


class RestHandler(BaseRequestHandler):
    """
    Request handler for rest applications
    """

    def initialize(self, model, object_depth=1, *args, **kwargs):
        """
        :param model: mongoengine Document subclass.
        :param object_depth: depth of the object, meaning how many
                             levels of RelatedFields will be returned.
                             Defaults to 1.

        Initializes object_depth and call initialize_extra_handlers().
        """
        super(RestHandler, self).initialize(model, *args, **kwargs)
        self.object_depth = object_depth
        self.operations = {'list': self.list_objects,
                           'get': self.get_object,
                           'put': self.put_object,
                           'delete': self.delete_object}

        # allowed operations by request method
        self.allowed_operations = {'get': ['get', 'list'],
                                   'post': ['put', 'delete'],
                                   'put': ['put'],
                                   'delete': ['delete'],
                                   'options': ['options']}

        # extra handlers used with EmbeddedDocuments and ListFields
        self.initialize_extra_handlers()

    def prepare(self):
        """
        Initializes json_extra_params which will be update()'d into
        the response json and get its pagination info needed for
        listing things
        """
        self.pagination = self._get_pagination()
        self.order_by = self._get_order_by()
        self.callback = self.get_callback()
        super(RestHandler, self).prepare()
        self.json_extra_params = {}

    def get(self, operation):
        """
        Called on GET requests
        """
        # operations allowed for this method (get)
        allowed_operations = self.get_allowed_operations('get')
        operation = operation or 'get'

        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self.call_method_and_write_json(method_to_call)

    def post(self, operation):
        """
        Called on POST requests
        """

        allowed_operations = self.get_allowed_operations('post')
        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self.call_method_and_write_json(method_to_call)

    def put(self, operation):
        """
        Called on PUT requests
        """
        allowed_operations = self.get_allowed_operations('put')
        operation = operation or 'put'
        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self.call_method_and_write_json(method_to_call)

    def delete(self, operation):
        """
        Called on DELETE requests
        """
        allowed_operations = self.get_allowed_operations('delete')
        operation = operation or 'delete'
        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self.call_method_and_write_json(method_to_call)

    def options(self, operation):
        """
        Method called on OPTIONS requests.
        """
        returned = self.send_options(*self.params)
        self.write(returned)

    def call_method_and_write_json(self, method_to_call):
        """
        Call the method for the requested action and writes
        the json response.

        :param method_to_call: callable which receives self.params as params.
        """
        returned_obj = method_to_call(**self.params)
        converter = get_converter(returned_obj, max_depth=self.object_depth)
        mydict = converter.sanitize_dict(converter.to_dict())
        mydict.update(self.json_extra_params)
        self.write(mydict)

    def write(self, chunk):
        if self.callback:
            chunk = self._get_jsonp(chunk, self.callback)
        return super(RestHandler, self).write(chunk)

    @classmethod
    def embeddedhandler(cls):
        return EmbeddedDocumentHandler

    def initialize_extra_handlers(self):
        if self.model_embedded_documents:
            pass

    def send_options(self, **kwargs):
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Methods',
                        'GET, POST, PUT, DELETE, OPTIONS')
        return {'corsEnabled': True}

    def list_objects(self, **kwargs):
        """
        Method that returns a list of objects. Called by
        get()
        """
        # removing lists from args passed to filter()
        clean_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, list):
                value = value[0]
            clean_kwargs[key] = value

        objects = self.model.objects.filter(**clean_kwargs)
        for order in self.order_by:
            objects.order_by(order.decode())

        total_items = len(objects)
        extra = {'total_items': total_items}
        self.json_extra_params.update(extra)
        return objects[self.pagination['ini']:self.pagination['end']]

    def get_object(self, **kwargs):
        """
        Returns a single object. Called by get()
        """
        return self.model.objects.get(**kwargs)

    def put_object(self, **kwargs):
        """
        Creates or update an object in database. Called by
        put() or post()
        """
        obj = self.model(**kwargs)
        obj.save()
        return obj

    def delete_object(self, **kwargs):
        """
        deletes an object. Called by delete()
        """
        obj = self.get_object(**kwargs)
        obj.delete()
        return obj

    def get_allowed_operations(self, method):
        """
        Returns the allowed operations for a particular
        method
        """
        return self.allowed_operations[method]

    def get_callback(self):
        """
        Returns the callback name to be used on jsonp requests
        """
        callback = self.request.arguments.get('callback') or None
        if callback:
            callback = callback[0]
            try:
                callback = callback.decode()
            except AttributeError:
                pass
        try:
            del self.request.arguments['callback']
        except KeyError:
            pass
        return callback

    def _validade_operation(self, operation, allowed_operations):
        if not operation in self.operations.keys():
            raise HTTPError(404)
        if not operation in allowed_operations:
            raise HTTPError(405)
        return self.operations[operation]

    def _get_jsonp(self, chunk, callback):
        mystr = str(chunk)
        jsonp = '%s(%s)' % (callback, mystr)
        return jsonp

    def _get_pagination(self):
        """
        Get pagination parameters from requets' arguments
        """
        max_items = int(self.request.arguments.get('max', [10])[0])
        page = int(self.request.arguments.get('page', [1])[0])
        try:
            del self.request.arguments['max']
        except KeyError:
            pass
        try:
            del self.request.arguments['page']
        except KeyError:
            pass
        ini = (page - 1) * max_items
        end = ini + max_items
        pagination = {'ini': ini, 'end': end, 'max': max_items, 'page': page}
        return pagination

    def _get_order_by(self):
        order_by = self.request.arguments.get('order_by', [])
        try:
            del self.request.arguments['order_by']
        except KeyError:
            pass
        return order_by


class ReadOnlyRestHandler(RestHandler):
    def post(self, operation):
        raise HTTPError(405)

    def put(self, operation):
        raise HTTPError(405)

    def delete(self, operation):
        raise HTTPError(405)


class EmbeddedDocumentHandler(RestHandler):
    def initialize(self, parent_doc, model, object_depth=1, *args, **kwargs):
        super(EmbeddedDocumentHandler, self).initialize(model, object_depth)
        self.parent_doc = parent_doc
        self.parsed_parent = get_parser(self.parent_doc).parse()

    def prepare(self):
        super(EmbeddedDocumentHandler, self).prepare()
        self.parent_id = self._get_parent_id()
        self.parent = self.parent_doc.objects.get(id=self.parent_id)

    def put_object(self, **kwargs):
        embed = self.model(**kwargs)

        field_name = self._get_field_name()
        # if its a listfield, verify if has something
        # already in list. If not, create a new one.
        if self.parsed_parent.get('list_fields') and \
           self.model in self.parsed_parent.get('list_fields').values():
            list_values = getattr(self.parent, field_name)
            if list_values:
                list_values.append(embed)
            else:
                list_values = [embed]
            setattr(self.parent, field_name, list_values)
        # if its not a list, set the object as the attribute
        else:
            setattr(self.parent, field_name, embed)

        self.parent.save()
        return embed

    def list_objects(self, **kwargs):
        field_name = self._get_field_name()
        objects_list = getattr(self.parent, field_name)
        total_items = len(objects_list)
        extra = {'total_items': total_items}
        self.json_extra_params.update(extra)
        return objects_list[self.pagination['ini']:self.pagination['end']]

    @classmethod
    def embeddedhandler(cls):
        return cls

    def _get_parent_id(self):
        try:
            parent_id = self.params['parent_id']
        except KeyError:
            raise HTTPError(500, 'parent_id param is required')
        del self.params['parent_id']
        return parent_id

    def _get_field_name(self):
        """
        Returns the field name for this embedded document
        in the parent_doc
        """

        name = None
        if self.parsed_parent.get('list_fields'):
            for key, value in self.parsed_parent.get('list_fields').items():
                if value == self.model:
                    return key
        if self.parsed_parent.get('embedded_documents'):
            for key, value in self.parsed_parent.get(
                    'embedded_documents').items():
                if value == self.model:
                    return key

        return name


class StaticFileHandler(StaticFileHandlerTornado):
    def initialize(self, static_dirs, default_filename=None):
        self.root = None
        type(self).static_dirs = static_dirs
        self.default_filename = default_filename

    @classmethod
    def get_absolute_path(cls, root, path):
        for root in cls.static_dirs:
            cls.static_root = root
            abspath = os.path.abspath(os.path.join(root, path))
            if os.path.exists(abspath):
                break
        return abspath

    def validate_absolute_path(self, root, absolute_path):
        self.root = self.static_root
        return super(StaticFileHandler, self).validate_absolute_path(
            self.root, absolute_path)


def get_rest_handler(obj, parent=None):
    if issubclass(obj, Document):
        return RestHandler
    elif issubclass(obj, EmbeddedDocument):
        if not parent:
            raise PyrocumulusException(
                'a parent is needed for an EmbeddedDocument')
        return EmbeddedDocumentHandler
    raise PyrocumulusException('rest handler not found for %s' % str(obj))
