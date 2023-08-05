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


from tornado.web import RequestHandler, HTTPError, Application
from pyrocumulus.converters import get_converter, get_request_converter
from pyrocumulus.parsers import get_parser


class BaseRestHandler(RequestHandler):
    def initialize(self, model, object_depth=1):
        """
        Initializes the model, set its referenced field and
        set the allowed operations for this handler.

        If you want to extend it, call super() first.
        """
        self.model = model
        self.object_depth = object_depth
        self.operations = {'list': self.list_objects,
                           'get': self.get_object,
                           'put': self.put_object,
                           'delete': self.delete_object}

        parser = get_parser(self.model)
        self.parsed_model = parser.parse()
        self.model_reference_fields = self.parsed_model['reference_fields']
        self.model_embedded_documents = self.parsed_model['embedded_documents']
        self.model_list_fields = self.parsed_model['list_fields']
        # extra handlers used with EmbeddedDocuments and ListFields
        self.initialize_extra_handlers()

    def prepare(self):
        """
        Called in the beginnig of every request.
        Initializes the params to be passed to self.model.objects,
        pagination params and json_extra_params.

        If you want to extend it, call super() first.
        """
        self.params = self._prepare_arguments()
        self.pagination = self._get_pagination()
        # these extra params are update()'d into
        # the json response dict
        self.json_extra_params = {}

    def get(self, operation):
        """
        Called on GET requests
        """
        # operations allowed for this method (get)
        allowed_operations = ['get', 'list']
        operation = operation or 'get'

        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self.call_method_and_write_json(method_to_call)

    def post(self, operation):
        """
        Called on POST requests
        """

        allowed_operations = ['put', 'delete']
        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self.call_method_and_write_json(method_to_call)

    def put(self, operation):
        """
        Called on PUT requests
        """
        allowed_operations = ['put']
        operation = operation or 'put'
        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self.call_method_and_write_json(method_to_call)

    def delete(self, operation):
        """
        Called on DELETE requests
        """
        allowed_operations = ['delete']
        operation = operation or 'delete'
        method_to_call = self._validade_operation(operation,
                                                  allowed_operations)
        self.call_method_and_write_json(method_to_call)

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

    def initialize_extra_handlers(self):
        if self.model_embedded_documents:
            pass

    def list_objects(self, **kwargs):
        """
        Method that returns a list of objects. Called by
        get()
        """
        # removing lists from args to filter()
        clean_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, list):
                value = value[0]
            clean_kwargs[key] = value

        objects = self.model.objects.filter(**clean_kwargs)
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
        converter = get_request_converter(self.request.arguments, self.model)
        return converter.to_dict()

    def _get_pagination(self):
        """
        Get pagination parameters from requets' arguments
        """
        max_items = int(self.request.arguments.get('max', [10])[0])
        page = int(self.request.arguments.get('page', [1])[0])
        ini = (page - 1) * max_items
        end = ini + max_items
        pagination = {'ini': ini, 'end': end, 'max': max_items, 'page': page}
        return pagination


class RestHandler(BaseRestHandler):
    pass


class ReadOnlyRestHandler(BaseRestHandler):
    def post(self, operation):
        raise NotImplementedError

    def put(self, operation):
        raise NotImplementedError

    def delete(self, operation):
        raise NotImplementedError


class EmbeddedDocumentHandler(BaseRestHandler):
    def initialize(self, parent_doc, model, object_depth=1):
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


class RestApplication(Application):
    def __init__(self, *models):
        self.request_handler = RestHandler
        self.models = models
        self._mappings = None
        super(RestApplication, self).__init__(self.mappings, debug=True)

    @property
    def mappings(self):
        if self._mappings:
            return self._mappings
        self._mappings = self._map_urls()
        return self._mappings

    def _map_urls(self):
        mappings = []
        for model in self.models:
            parser = get_parser(model)
            parsed_model = parser.parse()

            embedded_documents = parsed_model.get('embedded_documents')
            if embedded_documents:
                mappings += self._map_embedded_documents_urls(
                    model, embedded_documents)

            url = ('/api/%s/(.*)' % model.__name__.lower(),
                   self.request_handler, dict(model=model))
            mappings.append(url)

        return mappings

    def _map_embedded_documents_urls(self, model, embedded_documents):
        embedded_urls = []
        for name, embedded_document in embedded_documents.items():
            base_url = '/api/%s/%s/(.*)' % (
                model.__name__.lower(), name)
            url = (base_url, EmbeddedDocumentHandler,
                   dict(parent_doc=model, model=embedded_document))
            embedded_urls.append(url)
        return embedded_urls
